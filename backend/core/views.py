from django.shortcuts import render
from django.http import JsonResponse
from .models import Article
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from openai import OpenAI
import re


def home(request):
    return render(request, 'home.html')

def get_articles_by_category(request):
    print("get_articles_by_category")
    source = request.GET.get('source')
    category = request.GET.get('category')

    if not source or not category:
        return JsonResponse({"error": "缺少來源或分類參數"}, status=400)

    articles = Article.objects.filter(source=source, category=category).order_by('-published_at')[:10]

    data = [{
        'title': article.title,
        'summary': article.summary,
        'content': article.content,
        'url': article.url,
        'category': article.category,
        'published_at': article.published_at.strftime('%Y-%m-%d %H:%M'),
    } for article in articles]

    return JsonResponse(data, safe=False)

# 網址: https://api.laozhang.ai/
LAOZHANG_API_KEYS = [
    "sk-XZOM86ImafdhclzI267fDd5eEfD94717A70bD6DbB7D899A1", # pardeep15
    "sk-nGuEGXAvmPBp3ICW7fC6EaD635C6432a86A46cD38837F367", # usg1l
    "sk-X4jOQt8d6Gqygrt299B945A84163491c90B15dB7F0352290", # woyapik494
    "sk-yyJ2Cxg4FlGUiyWTB3F396FeCcC6427798F27c24020bD577", # chevonne.72
    "sk-LRJ147WrEMXlyxgv2aA86a4b5e8b45949bE24a70024f2951", # neofqxqs
    "sk-ViLG6Ho69IKbnoVS7c9fB32380C84aAdA8A12cC573C497B8", # duj0xmlh
    "sk-f0baX7OE1LuCRHI66230383665264977965c9c5d93C94002", # peugeot
    "sk-DkYe93FShvyPGVC0A043AaF3767f4a309aB34a4174FfE008", # karema92 
]
def chat_with_laozhang(messages, model="deepseek-v3"):
    base_url = "https://api.laozhang.ai/v1"

    for key in LAOZHANG_API_KEYS:
        try:
            client = OpenAI(api_key=key, base_url=base_url)
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"[!] API key 失敗：{key[:10]}...，錯誤：{e}")
            continue

    return "OpenAI 額度用完了 QQ"

@csrf_exempt
def generate_questions(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    data = json.loads(request.body)
    title = data.get('title')
    content = data.get('content')
    question_type = data.get('type')

    # prompt = build_prompt(title, content, question_type)

    try:
        if question_type == "reading":
            prompt = f"""
You are a question generation expert.

Based on the article below, generate 4 single-choice reading comprehension questions. 
Each question should have 4 options (A, B, C, D) and only one correct answer.
For each question, also provide a detailed explanation of why the answer is correct.

Return the result in valid JSON format, using the following structure:

{{
  "questions": [
    {{
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "answer": "...",
      "explanation": "..."
    }},
    ...
  ]
}}

Article Title: {title}

Article Content:
{content}
"""
        elif question_type == "cloze":
            prompt = f"""
You are an expert in designing cloze test (fill-in-the-blank) questions for English learners.

Your task is to create 4 cloze test questions using **only sentences taken directly from the article below**.

For each question:
- Select **one complete, unmodified sentence** from the article.
- Blank out **exactly one key word** using `______`.
- The blanked word should be **semantically important**, and **have only one clearly correct answer** in context.
- The correct answer should be **obvious to a proficient reader**, based on:
  - **Grammar rules** (e.g., verb tense, subject-verb agreement)
  - **Collocations or idiomatic usage**
  - **Semantic logic** (meaning within the sentence or paragraph)
- Avoid general or vague words like "have", "do", "get", or "make" unless the context clearly eliminates ambiguity.
- Provide **4 options** (A, B, C, D), with **only one best answer** that fits **both grammatically and logically**.
- The correct answer must match one of the options exactly.
- Include a **brief explanation**:
  - Why the correct answer fits best.
  - Why each of the other options is incorrect in this context.

Then, return a version of the article with the same 4 words blanked out in the original locations.  
Each blank should be replaced by `(n) ______` where `n` is the question number (1 to 4), matching the order of the questions.  
For example, the first blank is `(1) ______`, the second blank is `(2) ______`, and so on.

⚠️ VERY IMPORTANT:
- Do NOT write your own sentences.
- Do NOT blank vague or generic words.
- Do NOT create blanks that have more than one plausible answer.
- Each blank should have **only one contextually and grammatically correct answer**.

### Output Format:
Return valid JSON in the following structure:

{{
  "article_cloze": "...",   // The original article with the 4 target words replaced by `(n) ______`
  "questions": [
    {{
      "sentence": "...",           // The original sentence with one word replaced by `(n) ______`
      "options": ["...", "...", "...", "..."],
      "answer": "...",
      "explanation": "..."
    }},
    ...
  ]
}}

### Article Title:
{title}

### Article Content:
{content}
"""
        print(prompt)

        # # Step 2: AI分析
        messages=[
            {"role": "system", "content": "You are a english question generation expert"},
            {"role": "user", "content": prompt}
        ]
        # summary = chat_with_openrouter(messages)
        summary = chat_with_laozhang(messages)
        print("AI 回答：", summary)
        try:
            match = re.search(r'\{[\s\S]*\}', summary)
            if match:
                questions = json.loads(match.group())
            else:
                questions = {"questions": []}
        except Exception as e:
            return JsonResponse({"error": "JSON parsing failed", "raw": summary}, status=500)

        return JsonResponse({
            "article_content": content,
            "questions": questions["questions"]
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def build_prompt(title, content, question_type):
    if question_type == 'mc':
        return f"請根據以下新聞幫我出一道選擇題，附上4個選項和正確答案。\n\n標題：{title}\n\n內容：{content}"
    elif question_type == 'short':
        return f"請根據以下新聞幫我出一道簡答題。\n\n標題：{title}\n\n內容：{content}"
    elif question_type == 'summary':
        return f"請幫我為以下新聞設計一個摘要題，讓學生練習總結內容。\n\n標題：{title}\n\n內容：{content}"
    else:
        return f"請根據以下新聞設計一題閱讀理解題目。\n\n標題：{title}\n\n內容：{content}"
