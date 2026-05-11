import os
import random
from openai import OpenAI
from django.conf import settings

class DeepSeekService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
    
    def _get_mode_prompt(self, mode):
        """Возвращает промпт в зависимости от режима"""
        modes = {
            'cynic': {
                'personality': "Ты — циник и скептик. Немного ехидный, но не злой. Любишь говорить горькую правду.",
                'style': "используй сарказм, ироничные сравнения, циничные наблюдения. Пиши коротко, остро, с лёгкой издевкой."
            },
            'kind': {
                'personality': "Ты — добрый и заботливый друг. Мягкий, поддерживающий, но честный.",
                'style': "используй тёплые, поддерживающие фразы. Будь мягким, но убедительным. Проявляй эмпатию."
            },
            'devil': {
                'personality': "Ты — адвокат дьявола. Любишь спорить, провоцировать, смотреть с неожиданной стороны.",
                'style': "используй провокационные вопросы, неожиданные повороты, спорные утверждения. Бросай вызов очевидному."
            },
            'lazy': {
                'personality': "Ты — ленивец. Всё, что требует усилий, кажется тебе сомнительным. Любишь комфорт и отдых.",
                'style': "используй аргументы в пользу безделья, отдыха, минимальных усилий. Подсвечивай сложность любого действия."
            }
        }
        return modes.get(mode, modes['cynic'])
    
    def generate_counter_arguments(self, option_a, option_b, winner, mode='cynic'):
        """
        Генерирует 3 уникальных аргумента в выбранном режиме
        """
        mode_config = self._get_mode_prompt(mode)
        
        # Разные стили промптов для разнообразия
        prompt_styles = [
            "приведи 3 неожиданных, но правдивых аргумента",
            "напиши 3 причины, которые заставят задуматься",
            "сформулируй 3 контраргумента с юмором",
            "предложи 3 нестандартных взгляда на ситуацию",
            "дай 3 провокационных, но логичных довода",
            "приведи 3 аргумента, о которых пользователь не подумал",
            "напиши 3 причины с неожиданной стороны",
            "предложи 3 оригинальных контраргумента",
            "дай 3 свежих взгляда на эту ситуацию"
        ]
        
        # Выбираем случайный стиль
        style_choice = random.choice(prompt_styles)
        
        # СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ЛЕНИВЦА
        if mode == 'lazy':
            lazy_keywords = ['спать', 'отдых', 'диван', 'лежать', 'ничего', 'дома', 'остаться', 'лечь', 'поспать', 'сон', 'кровать']
            
            if any(kw in option_a.lower() for kw in lazy_keywords):
                lazy_choice = option_a
            elif any(kw in option_b.lower() for kw in lazy_keywords):
                lazy_choice = option_b
            else:
                lazy_choice = winner
            
            prompt = f"""
{mode_config['personality']}

Пользователь выбирает между:
А: {option_a}
Б: {option_b}

Твоя задача: {style_choice}
Убеди пользователя выбрать вариант "{lazy_choice}" (связан с отдыхом, бездельем).

Правила:
- Используй разные формулировки каждый раз
- Не повторяйся
- Каждый аргумент — одно предложение (10-15 слов)
- Без шаблонных фраз

Напиши 3 аргумента, каждый с новой строки.
"""
        else:
            opposite = option_b if winner == option_a else option_a
            
            prompt = f"""
{mode_config['personality']}

Пользователь выбирает между:
А: {option_a}
Б: {option_b}
Монетка показала: {winner}

Твоя задача: {style_choice}
Аргументы должны быть ЗА ПРОТИВОПОЛОЖНЫЙ вариант: {opposite}

Правила:
- Используй разные формулировки каждый раз
- Не повторяй те же аргументы, что в прошлый раз
- Каждый аргумент — одно предложение (10-15 слов)
- Будь оригинальным, избегай шаблонов

Напиши 3 аргумента, каждый с новой строки.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": f"Ты — {mode_config['personality']} Твоя задача — каждый раз придумывать новые, оригинальные аргументы. Никогда не повторяйся. Используй разные обороты, примеры, аналогии."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.95,  # Высокая температура для вариативности
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            arguments = [arg.strip() for arg in content.split('\n') if arg.strip()]
            arguments = [arg.lstrip('*-•123456789. ') for arg in arguments]
            
            # Фильтруем слишком короткие или пустые аргументы
            arguments = [arg for arg in arguments if len(arg) > 10]
            
            # Если получилось меньше 3 аргументов, добираем из fallback
            if len(arguments) < 3:
                fallback = [
                    f"Подумай ещё раз о {opposite}",
                    f"Возможно, {opposite} — это то, что нужно",
                    f"Не торопись с выбором"
                ]
                arguments.extend(fallback[:3 - len(arguments)])
            
            return arguments[:3]
            
        except Exception as e:
            print(f"DeepSeek ошибка: {e}")
            return None
    
    def generate_provocative_question(self, opposite, mode='cynic'):
        """Генерирует провокационный вопрос в выбранном режиме"""
        mode_config = self._get_mode_prompt(mode)
        
        # Разные варианты вопросов для разнообразия
        question_styles = [
            f"Как думаешь, что будет, если выбрать {opposite}?",
            f"А ты уверен, что {opposite} — правильный выбор?",
            f"Что тебя пугает в варианте {opposite}?",
            f"А если попробовать {opposite}? Что плохого может случиться?"
        ]
        
        if mode == 'lazy':
            prompt = f"""
{mode_config['personality']}
Придумай один короткий вопрос, который заставит задуматься о преимуществах бездействия и отдыха.
Вопрос должен быть с юмором, но не обидным.

Примеры:
- "А может, лучше ничего не делать и не пожалеть?"
- "Ты уверен, что готов к лишним движениям?"
- "Разве отдых — это не то, чего ты заслуживаешь?"

Ответь ТОЛЬКО вопросом, без кавычек и лишнего текста.
"""
        else:
            prompt = f"""
{mode_config['personality']}
Придумай один короткий, {mode_config['style'].replace('используй', '')}
Вопрос для человека, который думает выбрать вариант: "{opposite}"

Вопрос должен заставить его задуматься в рамках твоего режима.

Ответь ТОЛЬКО вопросом, без кавычек и лишнего текста.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": f"Ты — {mode_config['personality']}"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=100
            )
            
            question = response.choices[0].message.content.strip()
            return question
            
        except Exception as e:
            print(f"DeepSeek вопрос ошибка: {e}")
            return random.choice(question_styles)

    # ========== МЕТОДЫ ДЛЯ AI-ПСИХОЛОГА ==========

    def continue_therapy_dialogue(self, user_message, context, round_num):
        """
        Продолжает диалог с пользователем
        """
        history_text = ""
        if context['history']:
            last_messages = context['history'][-6:]
            history_text = "\n".join(last_messages)
        
        prompt = f"""Ты — эмпатичный психолог-консультант. Твоя задача — помочь пользователю разобраться в его дилемме.

Дилемма пользователя: выбрать между "{context['option_a']}" и "{context['option_b']}"

История диалога:
{history_text}

Новое сообщение пользователя: {user_message}
Текущий раунд: {round_num} из 5

Правила ответа:
1. Прояви эмпатию и понимание
2. Ответь 2-3 предложениями
3. Задай один уточняющий вопрос
4. Не давай готовых решений
5. Будь естественным, как живой собеседник

Твой ответ:"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": "Ты — эмпатичный психолог. Отвечай коротко, по делу, всегда заканчивай вопросом. Не используй markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=250
            )
            result = response.choices[0].message.content.strip()
            print(f"DeepSeek ответ психолога: {result[:100]}...")
            return result
        except Exception as e:
            print(f"Therapy dialogue error: {e}")
            return f"Я слышу тебя. Расскажи ещё, что ты чувствуешь по этому поводу?"

    def generate_therapy_conclusion(self, context, full_history):
        """
        Генерирует итоговый вывод после 5 раундов диалога
        """
        prompt = f"""Ты — профессиональный психолог. Проанализируй диалог с пользователем.

Дилемма пользователя: "{context['option_a']}" или "{context['option_b']}"

Вот что происходило в диалоге:
{full_history}

На основе этого диалога напиши:

**Вывод:** (что на самом деле беспокоит пользователя, какие его истинные страхи или желания)

**Совет:** (одно конкретное действие, которое можно сделать прямо сейчас)

**Поддержка:** (короткая ободряющая фраза)

Пиши по делу, без общих фраз. Будь конкретен к этой ситуации."""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": "Ты — психолог. Анализируй конкретную ситуацию пользователя. Не используй шаблонные фразы."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            result = response.choices[0].message.content.strip()
            print(f"DeepSeek вывод: {result[:200]}...")
            return result
        except Exception as e:
            print(f"Therapy conclusion error: {e}")
            return self._generate_fallback_conclusion(context, full_history)

    def _generate_fallback_conclusion(self, context, full_history):
        """Генерирует уникальный вывод без DeepSeek"""
        history_lower = full_history.lower()
        
        if "раздража" in history_lower or "бесит" in history_lower:
            return """**Вывод:** Тебя раздражает сам процесс выбора, а не объекты выбора.

**Совет:** Отложи решение на 3 дня. Если желание не вернётся — значит, ни один вариант тебе не нужен.

**Поддержка:** Не обязательно выбирать. Иногда лучший ответ — «никакой»."""
        
        if "устал" in history_lower or "устала" in history_lower:
            return """**Вывод:** Твоя усталость мешает ясно видеть ситуацию.

**Совет:** Сначала восстанови силы — выспись, отдохни. К решению вернись через день.

**Поддержка:** Ты справишься. Сейчас главное — позаботиться о себе."""
        
        if "боюсь" in history_lower or "страх" in history_lower:
            return """**Вывод:** Тобой движет страх, а не логика.

**Совет:** Напиши список «что самое страшное может случиться» — страх уменьшится.

**Поддержка:** Страх — это нормально. Но он не должен управлять тобой."""
        
        if "подарок" in history_lower or "кружка" in history_lower or "плед" in history_lower:
            return """**Вывод:** Ты хочешь подарить не просто вещь, а тёплые воспоминания и заботу.

**Совет:** Выбери то, что лучше отражает ваши отношения. Кружка — для утреннего кофе вместе, плед — для вечерних обнимашек.

**Поддержка:** Любой подарок от сердца будет правильным."""
        
        return f"""**Вывод:** Ты колеблешься между "{context['option_a']}" и "{context['option_b']}", потому что оба варианта имеют значение для тебя.

**Совет:** Попробуй представить, что выбор уже сделан. Что ты чувствуешь через неделю?

**Поддержка:** Доверься своей интуиции. Она редко ошибается."""