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
        """Генерирует 3 уникальных аргумента в выбранном режиме"""
        mode_config = self._get_mode_prompt(mode)
        
        prompt_styles = [
            "приведи 3 неожиданных, но правдивых аргумента",
            "напиши 3 причины, которые заставят задуматься",
            "сформулируй 3 контраргумента с юмором",
            "предложи 3 нестандартных взгляда на ситуацию",
            "дай 3 провокационных, но логичных довода",
            "приведи 3 аргумента, о которых пользователь не подумал"
        ]
        
        style_choice = random.choice(prompt_styles)
        
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
- Не повторяй те же аргументы
- Каждый аргумент — одно предложение (10-15 слов)
- Будь оригинальным, избегай шаблонов

Напиши 3 аргумента, каждый с новой строки.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": f"Ты — {mode_config['personality']} Твоя задача — каждый раз придумывать новые, оригинальные аргументы. Никогда не повторяйся. Отвечай коротко, 1-2 предложения на аргумент."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.95,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            arguments = [arg.strip() for arg in content.split('\n') if arg.strip()]
            arguments = [arg.lstrip('*-•123456789. ') for arg in arguments]
            arguments = [arg for arg in arguments if len(arg) > 10]
            
            if len(arguments) < 3:
                fallback = [
                    f"Подумай ещё раз о {opposite if mode != 'lazy' else lazy_choice}",
                    f"Возможно, это именно то, что нужно",
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
        
        question_styles = [
            f"Как думаешь, что будет, если выбрать {opposite}?",
            f"А ты уверен, что {opposite} — правильный выбор?",
            f"Что тебя пугает в варианте {opposite}?"
        ]
        
        if mode == 'lazy':
            prompt = f"""
{mode_config['personality']}
Придумай один короткий вопрос (максимум 12 слов) о преимуществах безделья.

Ответь ТОЛЬКО вопросом, без кавычек.
"""
        else:
            prompt = f"""
{mode_config['personality']}
Придумай один вопрос (максимум 12 слов) для выбора "{opposite}".

Ответь ТОЛЬКО вопросом.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": f"Ты — {mode_config['personality']} Отвечай одним коротким вопросом, максимум 12 слов."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=150
            )
            
            question = response.choices[0].message.content.strip()
            # Обрезаем слишком длинный вопрос
            if len(question) > 100:
                question = question[:97] + "..."
            return question
            
        except Exception as e:
            print(f"DeepSeek вопрос ошибка: {e}")
            return random.choice(question_styles)

    # ========== МЕТОДЫ ДЛЯ AI-ПСИХОЛОГА (ОПТИМАЛЬНАЯ ДЛИНА) ==========

    def continue_therapy_dialogue(self, user_message, context, round_num):
        """
        Продолжает диалог с пользователем. Оптимальная длина - 2-4 предложения.
        """
        history_text = ""
        if context['history']:
            last_messages = context['history'][-6:]
            history_text = "\n".join(last_messages)
        
        prompt = f"""Ты — эмпатичный психолог-консультант.

Дилемма пользователя: выбрать между "{context['option_a']}" и "{context['option_b']}"

История диалога:
{history_text}

Новое сообщение пользователя: {user_message}
Текущий раунд: {round_num} из 5

Правила ответа:
- Прояви эмпатию и понимание
- Ответь 2-4 предложениями
- Задай один уточняющий вопрос
- Не давай готовых решений
- Будь естественным, как живой собеседник

Твой ответ:"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": "Ты — эмпатичный психолог. Отвечай 2-4 предложениями, всегда заканчивай вопросом. Будь естественным."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300  # Оптимальная длина
            )
            result = response.choices[0].message.content.strip()
            print(f"DeepSeek ответ психолога: {result[:100]}...")
            return result
        except Exception as e:
            print(f"Therapy dialogue error: {e}")
            return f"Я слышу тебя. Расскажи ещё, что ты чувствуешь по этому поводу?"

    def generate_therapy_conclusion(self, context, full_history):
        """
        Генерирует итоговый вывод. Оптимальная длина - 300-500 символов.
        """
        # Обрезаем историю, но не слишком сильно
        if len(full_history) > 2000:
            full_history = full_history[-1500:]
        
        prompt = f"""Ты — профессиональный психолог. Проанализируй диалог с пользователем.

Дилемма пользователя: "{context['option_a']}" или "{context['option_b']}"

Вот что происходило в диалоге:
{full_history}

На основе этого диалога напиши КРАТКИЙ вывод (3-5 предложений):

**Вывод:** (что на самом деле беспокоит пользователя, 1-2 предложения)

**Совет:** (одно конкретное действие, 1 предложение)

**Поддержка:** (короткая ободряющая фраза, 1 предложение)

Пиши по делу, без воды. Будь конкретен."""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": "Ты — психолог. Давай конкретные выводы по ситуации пользователя. Ответ должен быть 3-5 предложений. Не используй маркдаун с **, пиши обычным текстом."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=550  # Оптимальная длина для вывода
            )
            result = response.choices[0].message.content.strip()
            
            # Не обрезаем принудительно, но если слишком длинный - слегка подрезаем
            if len(result) > 600:
                result = result[:597] + "..."
            
            print(f"DeepSeek вывод: {result[:200]}...")
            return result
        except Exception as e:
            print(f"Therapy conclusion error: {e}")
            return self._generate_fallback_conclusion(context, full_history)

    def _generate_fallback_conclusion(self, context, full_history):
        """Генерирует fallback вывод оптимальной длины"""
        history_lower = full_history.lower()
        
        if "раздража" in history_lower or "бесит" in history_lower:
            return """Вывод: Тебя раздражает сам процесс выбора, а не объекты выбора. Ты устал от необходимости принимать решения.

Совет: Отложи решение на 3 дня. Если желание не вернётся — значит, ни один вариант тебе не нужен.

Поддержка: Не обязательно выбирать. Иногда лучший ответ — «никакой»."""
        
        if "устал" in history_lower or "устала" in history_lower:
            return """Вывод: Твоя усталость мешает ясно видеть ситуацию. Ты хочешь решить проблему, но сил недостаточно.

Совет: Сначала восстанови силы — выспись, отдохни. К решению вернись через день.

Поддержка: Ты справишься. Сейчас главное — позаботиться о себе."""
        
        if "боюсь" in history_lower or "страх" in history_lower:
            return """Вывод: Тобой движет страх, а не логика. Ты боишься последствий любого выбора.

Совет: Напиши список «что самое страшное может случиться» — страх уменьшится.

Поддержка: Страх — это нормально. Но он не должен управлять тобой."""
        
        return f"""Вывод: Ты колеблешься между "{context['option_a']}" и "{context['option_b']}", потому что оба варианта имеют значение для тебя. Ты боишься ошибиться.

Совет: Попробуй представить, что выбор уже сделан. Что ты чувствуешь через неделю?

Поддержка: Доверься своей интуиции. Она редко ошибается."""