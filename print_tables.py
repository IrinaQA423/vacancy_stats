from terminaltables import AsciiTable


def print_stats_table(results, title):
    table_data = [[
        'Язык',
        'Найдено вакансий',
        'Обработано вакансий',
        'Средняя зарплата'
    ]]

    sorted_languages = sorted(
        results.items(),
        key=lambda x: x[1]['vacancies_found'],
        reverse=True
    )

    for lang, stats in sorted_languages:
        table_data.append([
            lang, str(stats['vacancies_found']),
            str(stats['vacancies_processed']),
            str(stats['average_salary'])
        ])

    table = AsciiTable(table_data)
    table.title = title
    table.inner_heading_row_border = True
    table.inner_row_border = False

    return table.table
