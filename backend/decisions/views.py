from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import random
import hashlib
import time
from django.core.cache import cache
from django.db.models import Q
from .models import Decision, CachedResponse
from .deepseek_service import DeepSeekService

# Резервные аргументы для разных режимов
FALLBACK_ARGUMENTS = {
    'cynic': [
        "Твой мозг просто ищет лёгкий путь. Не поддавайся первому порыву.",
        "А что скажешь себе через год? Какой вариант не вызовет стыда?",
        "Оба варианта — компромисс. Выбирай сердцем, потом разберёшься.",
        "Спроси у трёх друзей. Если мнения разделятся — разницы почти нет.",
        "Есть третий вариант: ничего не менять и жалеть. Хочешь именно этого?",
    ],
    'kind': [
        "Послушай своё сердце — оно подскажет правильный путь.",
        "Какой вариант сделает тебя счастливее уже завтра?",
        "Ты заслуживаешь того, что приносит радость.",
        "Представь, что советуешь лучшему другу. Что выберешь для него?",
        "Иногда правильный выбор — тот, от которого теплеет внутри.",
    ],
    'devil': [
        "А что если все вокруг неправы, а прав только ты?",
        "Почему ты вообще доверяешь случайности свою судьбу?",
        "А вдруг это проверка на прочность, и ты должен поступить вопреки?",
        "Кто сказал, что выбор должен быть логичным?",
        "А может, тебя просто обманывают собственные страхи?",
    ],
    'lazy': [
        "Зачем напрягаться, если можно ничего не менять?",
        "Лучшее — враг хорошего. А хорошее — враг дивана.",
        "Подумай, сколько сил сэкономишь, если оставить всё как есть.",
        "Активность — это переоценено. Отдых — вот истинная ценность.",
        "Любое действие ведёт к усталости. А бездействие — к покою.",
    ],
}

FALLBACK_QUESTIONS = {
    'cynic': [
        "А уверен, что это не просто страх?",
        "Что бы сказал твой лучший друг?",
        "Сколько раз ты уже выбирал похожее и жалел?",
        "А если не получится — ты простишь себя?",
    ],
    'kind': [
        "Какой вариант ближе твоему сердцу?",
        "Что принесёт тебе больше радости?",
        "Что бы ты посоветовал близкому человеку?",
        "Какой выбор сделает тебя счастливее?",
    ],
    'devil': [
        "А что если всё наоборот?",
        "Почему ты вообще уверен, что прав?",
        "А вдруг тебя просто программируют на этот выбор?",
        "Кто выиграет от твоего решения, кроме тебя?",
    ],
    'lazy': [
        "А оно точно стоит твоих усилий?",
        "Может, проще ничего не менять?",
        "Ты уверен, что готов к последствиям?",
        "А если подождать — само рассосётся?",
    ],
}

class CoinFlipAPIView(APIView):
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        self.deepseek = None
        try:
            self.deepseek = DeepSeekService()
        except Exception as e:
            print(f"DeepSeek не инициализирован: {e}")
    
    def _get_cache_key(self, option_a, option_b, mode):
        text = f"{mode}|{option_a.lower()}|{option_b.lower()}"
        return f"decision_{hashlib.md5(text.encode()).hexdigest()}"
    
    def _find_similar_in_db(self, option_a, option_b, mode):
        exact = Decision.objects.filter(
            Q(option_a__iexact=option_a, option_b__iexact=option_b) |
            Q(option_a__iexact=option_b, option_b__iexact=option_a),
            mode=mode
        ).order_by('-created_at').first()
        
        if exact:
            return exact
        
        exact_any_mode = Decision.objects.filter(
            Q(option_a__iexact=option_a, option_b__iexact=option_b) |
            Q(option_a__iexact=option_b, option_b__iexact=option_a)
        ).order_by('-created_at').first()
        
        if exact_any_mode:
            return exact_any_mode
        
        return None
    
    def _check_user_limit(self, session_key):
        limit_key = f"user_limit_{session_key}"
        count = cache.get(limit_key, 0)
        
        if count >= 15:
            return False
        
        cache.set(limit_key, count + 1, 3600)
        return True
    
    def post(self, request):
        option_a = request.data.get('option_a', '').strip()
        option_b = request.data.get('option_b', '').strip()
        mode = request.data.get('mode', 'cynic').strip()
        
        if mode not in ['cynic', 'kind', 'devil', 'lazy']:
            mode = 'cynic'
        
        if not option_a or not option_b:
            return Response({'error': 'Оба варианта обязательны'}, status=400)
        
        request.session.create()
        session_key = request.session.session_key
        
        cache_key = self._get_cache_key(option_a, option_b, mode)
        cached_response = cache.get(cache_key)
        
        if cached_response:
            print(f"✅ КЭШ | {mode} | {option_a} vs {option_b}")
            decision = Decision.objects.create(
                option_a=option_a,
                option_b=option_b,
                coin_result=cached_response['coin_result'],
                counter_arguments=cached_response['counter_arguments'],
                provocative_question=cached_response.get('provocative_question', ''),
                session_key=session_key,
                mode=mode,
                from_cache=True
            )
            cached_response['decision_id'] = decision.id
            return Response(cached_response)
        
        similar = self._find_similar_in_db(option_a, option_b, mode)
        
        if similar:
            print(f"📚 БД | {mode} | {option_a} vs {option_b}")
            coin_result = random.choice([option_a, option_b])
            
            response_data = {
                'coin_result': coin_result,
                'counter_arguments': similar.counter_arguments,
                'provocative_question': similar.provocative_question or random.choice(FALLBACK_QUESTIONS.get(mode, FALLBACK_QUESTIONS['cynic']))
            }
            
            cache.set(cache_key, response_data, 86400)
            
            decision = Decision.objects.create(
                option_a=option_a,
                option_b=option_b,
                coin_result=coin_result,
                counter_arguments=similar.counter_arguments,
                provocative_question=response_data['provocative_question'],
                session_key=session_key,
                mode=mode,
                from_cache=True
            )
            response_data['decision_id'] = decision.id
            response_data['mode'] = mode
            return Response(response_data)
        
        has_limit = self._check_user_limit(session_key)
        
        coin_result = random.choice([option_a, option_b])
        opposite = option_b if coin_result == option_a else option_a
        
        arguments = None
        provocative_question = None
        used_deepseek = False
        
        if has_limit and self.deepseek:
            try:
                print(f"🤖 DeepSeek | {mode} | {option_a} vs {option_b}")
                arguments = self.deepseek.generate_counter_arguments(
                    option_a, option_b, coin_result, mode
                )
                provocative_question = self.deepseek.generate_provocative_question(opposite, mode)
                used_deepseek = True
            except Exception as e:
                print(f"❌ DeepSeek ошибка: {e}")
        
        if not arguments or len(arguments) < 3:
            arguments = random.sample(FALLBACK_ARGUMENTS.get(mode, FALLBACK_ARGUMENTS['cynic']), 3)
        
        if not provocative_question:
            provocative_question = random.choice(FALLBACK_QUESTIONS.get(mode, FALLBACK_QUESTIONS['cynic']))
        
        decision = Decision.objects.create(
            option_a=option_a,
            option_b=option_b,
            coin_result=coin_result,
            counter_arguments=arguments,
            provocative_question=provocative_question,
            session_key=session_key,
            mode=mode,
            used_deepseek=used_deepseek
        )
        
        response_data = {
            'decision_id': decision.id,
            'coin_result': coin_result,
            'counter_arguments': arguments,
            'provocative_question': provocative_question,
            'mode': mode
        }
        
        if used_deepseek:
            cache.set(cache_key, response_data, 86400)
        
        return Response(response_data)


# ========== AI-ПСИХОЛОГ ==========

class TherapyStartAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        option_a = request.data.get('option_a', '').strip()
        option_b = request.data.get('option_b', '').strip()
        
        if not option_a or not option_b:
            return Response({'error': 'Оба варианта обязательны'}, status=400)
        
        session_id = hashlib.md5(f"{option_a}|{option_b}|{time.time()}".encode()).hexdigest()
        
        context = {
            'option_a': option_a,
            'option_b': option_b,
            'history': [],
            'round_num': 1
        }
        cache.set(f"therapy_{session_id}", context, 3600)
        
        return Response({
            'session_id': session_id,
            'round': 1,
            'max_rounds': 5
        })


class TherapyChatAPIView(APIView):
    """Продолжает диалог с AI-психологом"""
    permission_classes = [AllowAny]
    max_rounds = 5
    
    def __init__(self):
        super().__init__()
        self.deepseek = None
        try:
            self.deepseek = DeepSeekService()
        except Exception as e:
            print(f"DeepSeek не инициализирован: {e}")
    
    def post(self, request):
        session_id = request.data.get('session_id')
        user_message = request.data.get('message', '').strip()
        current_round = request.data.get('round', 1)
        
        if not session_id:
            return Response({'error': 'session_id обязателен'}, status=400)
        
        context = cache.get(f"therapy_{session_id}")
        if not context:
            return Response({'error': 'Сессия не найдена или истекла'}, status=404)
        
        # Добавляем сообщение пользователя в историю
        context['history'].append(f"Пользователь: {user_message}")
        
        # Если это был последний ответ пользователя (5-й), завершаем
        if current_round >= self.max_rounds:
            return Response({
                'reply': '',
                'round': current_round + 1,
                'is_last_round': True,
                'max_rounds': self.max_rounds
            })
        
        # Генерируем ответ психолога
        reply = ""
        if self.deepseek:
            try:
                reply = self.deepseek.continue_therapy_dialogue(
                    user_message, context, current_round
                )
            except Exception as e:
                print(f"Ошибка генерации ответа: {e}")
                reply = "Расскажи подробнее, что ты чувствуешь?"
        
        if not reply:
            reply = "Понимаю. А что ты чувствуешь?"
        
        # Добавляем ответ в историю
        context['history'].append(f"Психолог: {reply}")
        
        # Сохраняем контекст
        cache.set(f"therapy_{session_id}", context, 3600)
        
        next_round = current_round + 1
        is_last_round = next_round > self.max_rounds
        
        return Response({
            'reply': reply,
            'round': next_round,
            'is_last_round': is_last_round,
            'max_rounds': self.max_rounds
        })


class TherapyConclusionAPIView(APIView):
    """Генерирует итоговый вывод психолога"""
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        self.deepseek = None
        try:
            self.deepseek = DeepSeekService()
        except Exception as e:
            print(f"DeepSeek не инициализирован: {e}")
    
    def post(self, request):
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response({'error': 'session_id обязателен'}, status=400)
        
        context = cache.get(f"therapy_{session_id}")
        if not context:
            return Response({'error': 'Сессия не найдена или истекла'}, status=404)
        
        full_history = "\n".join(context['history'])
        
        # Генерируем вывод через DeepSeek
        conclusion = ""
        if self.deepseek:
            try:
                conclusion = self.deepseek.generate_therapy_conclusion(context, full_history)
                print(f"DeepSeek вывод: {conclusion[:100]}...")
            except Exception as e:
                print(f"Ошибка генерации вывода: {e}")
                conclusion = None
        
        # Если DeepSeek не сработал, используем fallback
        if not conclusion:
            conclusion = self._generate_conclusion_from_history(full_history, context)
        
        cache.delete(f"therapy_{session_id}")
        
        return Response({
            'conclusion': conclusion
        })
    
    def _generate_conclusion_from_history(self, history, context):
        """Генерирует вывод на основе ключевых слов в истории"""
        history_lower = history.lower()
        
        # Еда
        if any(word in history_lower for word in ['бургер', 'шаурм', 'еда', 'съесть', 'голод', 'вкус']):
            return """**Вывод:** Твой выбор между бургером и шаурмой — это не просто про еду. Это про желание получить удовольствие, когда внутри пустота.

**Совет:** Съешь то, что первое пришло в голову. А может, попробуй оба варианта в разные дни.

**Поддержка:** Иногда маленький выбор — это просто выбор. Не нагружай его лишним смыслом."""
        
        # Боль и эмоции
        if any(word in history_lower for word in ['боль', 'пережива', 'тяжело', 'трудно']):
            return """**Вывод:** Твоя боль ищет выхода через простые бытовые решения. Выбор еды стал символическим.

**Совет:** Сначала разберись с тем, что вызывает боль. Выбор еды может подождать.

**Поддержка:** Ты не один. Позволь себе чувствовать и проживать эти эмоции."""
        
        # Работа
        if any(word in history_lower for word in ['работа', 'уйти', 'уволить', 'начальник']):
            return """**Вывод:** Твоя дилемма с работой — это сигнал, что что-то нужно менять.

**Совет:** Сделай маленький шаг: обнови резюме или поговори с руководителем.

**Поддержка:** Твои навыки ценятся. Новые возможности уже ждут."""
        
        # Отношения
        if any(word in history_lower for word in ['люблю', 'отношени', 'парень', 'девушк', 'друг']):
            return """**Вывод:** Отношения — это сложно. Твои сомнения говорят о том, что тебе важно сохранить себя.

**Совет:** Поговори откровенно. Иногда разговор решает больше, чем молчание.

**Поддержка:** Ты имеешь право на свои чувства и границы."""
        
        # Стандартный вывод на основе дилеммы
        return f"""**Вывод:** Ты колеблешься между "{context['option_a']}" и "{context['option_b']}", потому что оба варианта имеют для тебя значение.

**Совет:** Попробуй представить, что выбор уже сделан. Что ты чувствуешь через день?

**Поддержка:** Доверься себе. Любой выбор будет правильным, потому что он твой."""


# ========== НОВЫЙ КЛАСС С РАЗДЕЛЕНИЕМ ПО РЕЖИМАМ ==========

class CoinFlipWithCacheAPIView(APIView):
    """Версия с накоплением 20 ответов для КАЖДОГО РЕЖИМА отдельно"""
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        self.deepseek = None
        try:
            self.deepseek = DeepSeekService()
        except Exception as e:
            print(f"DeepSeek не инициализирован: {e}")
    
    def _is_unique_response(self, option_a, option_b, mode, arguments):
        """Проверяет, не существует ли уже такого же ответа"""
        existing = CachedResponse.objects.filter(
            option_a__iexact=option_a,
            option_b__iexact=option_b,
            mode=mode,
            counter_arguments=arguments
        ).exists()
        return not existing
    
    def post(self, request):
        option_a = request.data.get('option_a', '').strip()
        option_b = request.data.get('option_b', '').strip()
        mode = request.data.get('mode', 'cynic').strip()
        
        if not option_a or not option_b:
            return Response({'error': 'Оба варианта обязательны'}, status=400)
        
        if mode not in ['cynic', 'kind', 'devil', 'lazy']:
            mode = 'cynic'
        
        # Нормализуем порядок вариантов
        if option_a.lower() > option_b.lower():
            option_a, option_b = option_b, option_a
        
        # Ищем кэшированные ответы для ЭТОЙ дилеммы и ЭТОГО режима
        existing_responses = list(CachedResponse.objects.filter(
            option_a__iexact=option_a,
            option_b__iexact=option_b,
            mode=mode
        ))
        
        count = len(existing_responses)
        target_count = 200
        
        # Если накоплено достаточно - берём случайный (бесплатно!)
        if count >= target_count:
            print(f"✅ БД | Режим: {mode} | {option_a} vs {option_b} | Кэш ({count} вариантов)")
            cached = random.choice(existing_responses)
            cached.usage_count += 1
            cached.save()
            
            coin_result = random.choice([option_a, option_b])
            
            request.session.create()
            Decision.objects.create(
                option_a=option_a,
                option_b=option_b,
                coin_result=coin_result,
                counter_arguments=cached.counter_arguments,
                provocative_question=cached.provocative_question,
                session_key=request.session.session_key,
                mode=mode,
                from_cache=True
            )
            
            return Response({
                'coin_result': coin_result,
                'counter_arguments': cached.counter_arguments,
                'provocative_question': cached.provocative_question,
                'mode': mode,
                'from_cache': True,
                'cache_size': count,
                'message': f'Из кэша для режима {mode} ({count} вариантов)'
            })
        
        # Накоплено меньше 200 - вызываем DeepSeek
        print(f"🤖 DeepSeek | Режим: {mode} | {option_a} vs {option_b} | Накоплено: {count}/{target_count}")
        
        request.session.create()
        session_key = request.session.session_key
        
        coin_result = random.choice([option_a, option_b])
        opposite = option_b if coin_result == option_a else option_a
        
        arguments = None
        provocative_question = None
        
        # Пытаемся сгенерировать уникальный ответ (максимум 5 попыток)
        max_attempts = 5
        for attempt in range(max_attempts):
            if self.deepseek:
                try:
                    arguments = self.deepseek.generate_counter_arguments(
                        option_a, option_b, coin_result, mode
                    )
                    provocative_question = self.deepseek.generate_provocative_question(opposite, mode)
                except Exception as e:
                    print(f"❌ DeepSeek ошибка: {e}")
            
            if not arguments or len(arguments) < 3:
                arguments = random.sample(FALLBACK_ARGUMENTS.get(mode, FALLBACK_ARGUMENTS['cynic']), 3)
            
            if not provocative_question:
                provocative_question = random.choice(FALLBACK_QUESTIONS.get(mode, FALLBACK_QUESTIONS['cynic']))
            
            # Проверяем уникальность
            is_unique = self._is_unique_response(option_a, option_b, mode, arguments)
            
            if is_unique:
                print(f"✅ Уникальный ответ найден с попытки {attempt + 1}")
                break
            else:
                print(f"⚠️ Попытка {attempt + 1}: найден дубликат, генерируем заново...")
                arguments = None
        
        # Сохраняем ответ
        CachedResponse.objects.create(
            option_a=option_a,
            option_b=option_b,
            mode=mode,
            coin_result=coin_result,
            counter_arguments=arguments,
            provocative_question=provocative_question
        )
        
        Decision.objects.create(
            option_a=option_a,
            option_b=option_b,
            coin_result=coin_result,
            counter_arguments=arguments,
            provocative_question=provocative_question,
            session_key=session_key,
            mode=mode,
            used_deepseek=True
        )
        
        new_count = CachedResponse.objects.filter(
            option_a__iexact=option_a,
            option_b__iexact=option_b,
            mode=mode
        ).count()
        
        return Response({
            'coin_result': coin_result,
            'counter_arguments': arguments,
            'provocative_question': provocative_question,
            'mode': mode,
            'from_cache': False,
            'cache_size': new_count,
            'message': f'Сгенерировано для режима {mode} ({new_count}/{target_count})'
        })