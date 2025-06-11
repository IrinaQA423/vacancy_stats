from statistics import mean
import os

import requests
from dotenv import load_dotenv

from generate_tables import generate_stats_table


HH_API_AREA = 1
HH_API_PERIOD = 30
ITEMS_PER_PAGE = 100
SJ_API_TOWN = 4
SJ_API_CATALOGUE = 48


def fetch_all_vacancies_hh(language):
    hh_url = 'https://api.hh.ru/vacancies'
    all_vacancies = []
    page = 0
    total_pages = 1

    while page < total_pages:
        params = {
            'text': f'программист {language}',
            'area': HH_API_AREA,
            'period': HH_API_PERIOD,
            'page': page,
            'per_page': ITEMS_PER_PAGE
        }

        response = requests.get(hh_url, params=params)
        response.raise_for_status()
        hh_api_response = response.json()

        total_pages = hh_api_response['pages']
        all_vacancies.extend(hh_api_response['items'])
        page += 1

    return hh_api_response.get('found', 0), all_vacancies


def fetch_all_vacancies_sj(language, secret_key):
    superjob_url = 'https://api.superjob.ru/2.0/vacancies/'
    all_vacancies = []
    page = 0
    more_pages = True
    total_vacancies = 0

    headers = {'X-Api-App-Id': secret_key}

    while more_pages:
        params = {

            'keyword': f'программист {language}',
            'town': SJ_API_TOWN,
            'catalogues': SJ_API_CATALOGUE,
            'page': page,
            'count': ITEMS_PER_PAGE
        }

        response = requests.get(superjob_url, headers=headers,
                                params=params, timeout=10)
        response.raise_for_status()
        sj_api_response = response.json()

        all_vacancies.extend(sj_api_response.get('objects', []))
        if page == 0:
            total_vacancies = sj_api_response.get('total', 0)
            more_pages = sj_api_response.get('more', False)

            page += 1

    return total_vacancies, all_vacancies


def process_hh_vacancies(hh_result):
    found, hh_vacancies = hh_result

    if not hh_vacancies:
        return None

    salaries = []
    for vacancy in hh_vacancies:

        salary = predict_rub_salary_hh(vacancy)
        if salary:
            salaries.append(salary)

    avg_salary = int(mean(salaries)) if salaries else None

    return {
        "vacancies_found": found,
        "vacancies_processed": len(salaries),
        "average_salary": avg_salary
    }


def process_sj_vacancies(sj_result):
    found, sj_vacancies = sj_result

    if not sj_vacancies:
        return None

    salaries = []
    for vacancy in sj_vacancies:
        salary = predict_rub_salary_sj(vacancy)
        if salary:
            salaries.append(salary)

    avg_salary = int(mean(salaries)) if salaries else None

    return {
        "vacancies_found": found,
        "vacancies_processed": len(salaries),
        "average_salary": avg_salary
    }


def predict_rub_salary(salary_from, salary_to):

    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8
    return None


def predict_rub_salary_hh(vacancy):
    salary_data = vacancy.get('salary')

    if not salary_data or salary_data.get('currency') != 'RUR':
        return None
    return predict_rub_salary(
        salary_data.get('from'),
        salary_data.get('to')
    )


def predict_rub_salary_sj(vacancy):

    if not vacancy.get('payment_from') and not vacancy.get('payment_to'):
        return None
    if vacancy.get('currency') != 'rub':
        return None
    return predict_rub_salary(
        vacancy.get('payment_from'),
        vacancy.get('payment_to')
    )


def main():
    load_dotenv()

    sj_secret = os.getenv('SJ_SECRET_KEY')

    languages = [
        "Python",
        "Java",
        "Javascript",
        "C++",
        "C#",
        "PHP",
        "Go",
        "Kotlin",
        "Swift",
        "TypeScript",
        "Ruby",
        "1C"
    ]

    hh_results = {}
    sj_results = {}

    for lang in languages:
        hh_vacancies = fetch_all_vacancies_hh(lang)
        hh_stats = process_hh_vacancies(hh_vacancies)
        if hh_stats:
            hh_results[lang] = hh_stats

        sj_vacancies = fetch_all_vacancies_sj(lang, sj_secret)
        sj_stats = process_sj_vacancies(sj_vacancies)
        if sj_stats:
            sj_results[lang] = sj_stats

    output = [
        "\nСтатистика по вакансиям в Москве",
        generate_stats_table(hh_results, 'HeadHunter'),
        "",
        generate_stats_table(sj_results, 'SuperJob')
    ]

    print("\n".join(output))


if __name__ == '__main__':
    main()
