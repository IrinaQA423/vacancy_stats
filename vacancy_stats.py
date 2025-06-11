from statistics import mean
import os

import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv


def fetch_all_vacancies_hh(language):
    hh_url = 'https://api.hh.ru/vacancies' 
    all_vacancies = []
    page = 0
    pages_number = 1

    while page < pages_number:
        params = {
            'text': f'программист {language}',
            'area': 1,
            'period': 30,
            'page': page,
            'per_page': 100
        }

        page_response = requests.get(hh_url, params=params)
        page_response.raise_for_status()
        page_payload = page_response.json()

        pages_number = page_payload['pages']
        all_vacancies.extend(page_payload['items'])
        page += 1

    return {
        'found': page_payload.get('found', 0),
        'vacancies': all_vacancies
    }


def fetch_all_vacancies_sj(language, secret_key):
    superjob_url = 'https://api.superjob.ru/2.0/vacancies/'
    all_vacancies = []
    page = 0
    more_pages = True
    total = 0

    headers = {'X-Api-App-Id': secret_key}

    while more_pages:
        params = {

            'keyword': f'программист {language}',
            'town': 4,
            'catalogues': 48,
            'page': page,
            'count': 100
        }

        response = requests.get(superjob_url, headers=headers,
                                params=params, timeout=10)
        response.raise_for_status()
        vacancies_data = response.json()

        all_vacancies.extend(vacancies_data.get('objects', []))
        if page == 0:
            total = vacancies_data.get('total', 0)
            more_pages = vacancies_data.get('more', False)

        page += 1

    return {
        'found': total,
        'vacancies': all_vacancies
    }


def process_hh_vacancies(vacancies_data):
    #hh_url = 'https://api.hh.ru/vacancies' 
    #vacancies_data = fetch_all_vacancies_hh(language, hh_url)
    if not vacancies_data or not vacancies_data.get('vacancies'):
        return None

    salaries = []
    for vacancy in vacancies_data['vacancies']:

        salary = predict_rub_salary_hh(vacancy)
        if salary:
            salaries.append(salary)

    avg_salary = int(mean(salaries)) if salaries else None

    return {
        "vacancies_found": vacancies_data['found'],
        "vacancies_processed": len(salaries),
        "average_salary": avg_salary
    }


def process_sj_vacancies(vacancies_data):
    #superjob_url = 'https://api.superjob.ru/2.0/vacancies/'
    #vacancies_data = fetch_all_vacancies_sj(language, secret_key, superjob_url)
    if not vacancies_data or not vacancies_data.get('vacancies'):
        return None

    salaries = []
    for vacancy in vacancies_data['vacancies']:
        salary = predict_rub_salary_sj(vacancy)
        if salary:
            salaries.append(salary)

    avg_salary = int(mean(salaries)) if salaries else None

    return {
        "vacancies_found": vacancies_data['found'],
        "vacancies_processed": len(salaries),
        "average_salary": avg_salary
    }


def predict_rub_salary(salary_from, salary_to):

    if salary_from is not None and salary_to is not None:
        return (salary_from + salary_to) / 2
    elif salary_from is not None:
        return salary_from * 1.2
    elif salary_to is not None:
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


def print_sj_table(sj_results):
    table_data = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]]
    sorted_languages = sorted(
        sj_results.items(),
        key=lambda x: x[1]['vacancies_found'],
        reverse=True
    )
    for lang, stats in sorted_languages:
        table_data.append([
            lang,
            str(stats['vacancies_found']),
            str(stats['vacancies_processed']),
            str(stats['average_salary'])
        ])

    table = AsciiTable(table_data)
    table.title = 'SuperJob Moscow'
    table.inner_heading_row_border = True
    table.inner_row_border = False

    return table.table


def print_hh_table(hh_results):

    table_data = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]]

    sorted_languages = sorted(
        hh_results.items(),
        key=lambda x: x[1]['vacancies_found'],
        reverse=True
    )

    for lang, stats in sorted_languages:
        table_data.append([
            lang,
            str(stats['vacancies_found']),
            str(stats['vacancies_processed']),
            str(stats['average_salary'])
        ])

    table = AsciiTable(table_data)
    table.title = 'HeadHunter Moscow'
    table.inner_heading_row_border = True
    table.inner_row_border = False

    return table.table


def main():
    load_dotenv()

    #superjob_url = 'https://api.superjob.ru/2.0/vacancies/'
    #hh_url = 'https://api.hh.ru/vacancies'
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

    for lang in languages:
        vacancies = fetch_all_vacancies_hh(lang)
        stats = process_hh_vacancies(vacancies)
        if stats:
            hh_results[lang] = stats

    sj_results = {}
    for lang in languages:
        vacancies = fetch_all_vacancies_sj(lang,sj_secret)

        stats = process_sj_vacancies(vacancies)
        if stats:
            sj_results[lang] = stats

    output = [
        "\nСтатистика по вакансиям в Москве",
        print_hh_table(hh_results),
        "",
        print_sj_table(sj_results)
    ]
    
    print("\n".join(output))
    


if __name__ == '__main__':
    main()
