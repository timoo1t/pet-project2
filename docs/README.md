# UML-диаграммы

## technical.png — техническая (сверху вниз)

1. **Импорты** — все `import` из quiz_app.py  
2. **Пути** — `_resource_dir`, `_writable_dir`, константы APP_DIR…  
3. **FlaskApp** — приложение, secret_key, папки шаблонов  
4. **Question → AnswerRecord → SessionState** — структуры данных  
5. **questions.json, results.txt** — файлы  
6. **DataFunctions** — методы load/get/save  
7. **QuizRoutes** — маршруты index, start, question, answer, result, restart  
8. **Templates, style.css** — интерфейс  
9. **Main** — `__main__`, браузер, `app.run`  
10. **CycleStart → CycleLoop → CycleEnd** — цикл викторины (шаги 1–22)

## user.png — пользовательская (сверху вниз)

Шаги 1–17: запуск → старт → цикл вопросов → результат → повтор или выход.

## Пересборка

```bash
cd docs
python generate_png.py
```
