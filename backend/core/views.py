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
    category = request.GET.get('category')
    if not category:
        return JsonResponse({"error": "缺少分類參數"}, status=400)

    articles = Article.objects.filter(category=category).order_by('-published_at')[:10]

    data = []
    for article in articles:
        data.append({
            'title': article.title,
            'summary': article.summary,
            'content': article.content,
            'url': article.url,
            'category': article.category,
            'published_at': article.published_at.strftime('%Y-%m-%d %H:%M'),
        })

    return JsonResponse(data, safe=False)

# 網址: https://api.laozhang.ai/
LAOZHANG_API_KEYS = [
    "sk-EchQx6n2KD2XfleCB9590c4b2bBc49B2Bf7b6aA8C673D995", # j199180305
    "sk-8bwyGOF3gFUvTsRhD3581b0069Dc49A4806c03E999127934", # ga2006144505
    "sk-8bwyGOF3gFUvTsRhD3581b0069Dc49A4806c03E999127934", # ga2006144505
    "sk-1L7qavnrVUVcDZyf5aB906B5Cd06427b8f5826F5A727Cc33", # csun3366
    "sk-wusLtqT5U1g5m8kmD53a67C0E5Be4fCd82939d45F99b34Cc", # llvmphighter
    "sk-PCdQaYOW3mLb5tu22d9f891b66934771A7EfBe9e4b3527F8", # yuanhan132
    "sk-Z98Bp3JWYGKp6nkW041140DfF6274999A4833bF7D7985955", # shannie132
    "sk-cCGMSSzE82mLEQ8m1fB88746D6874219AeE0Fd8b7b4942Cb", # jmotor047
    "sk-JRtt6ZJ1QFvigS3G56FdB74bEcEc435493Bd32E9C34466De", # woyang84
    "sk-adwTZ7MUxpICWiaT717d71E086E54161904a1eAb82682dCf", # hoh873700
    "sk-SmEEDCKQ7lx4sGSd9aFcEc4638A74440A94b618508Be32D8", # frenchplum
    "sk-BOBJ2be4bf02IukGEb3748C4Af724eBf8163298747761786", # waterspouta0
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
        questions = {
        "questions": [
            {
            "question": "What did the U.S. president emphasize in the speech?",
            "options": ["Multilateral cooperation", "Unilateralism", "Economic sanctions", "Military intervention"],
            "answer": "Multilateral cooperation"
            },
            {
            "question": "How effective is the new generation vaccine?",
            "options": ["Effectively controls the virus", "Ineffective", "Under research", "Severe side effects"],
            "answer": "Effectively controls the virus"
            }
        ]
        }

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
