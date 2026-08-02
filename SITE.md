# Сайт-портфолио переехал

Исходники [igorkhaylov.uz](https://igorkhaylov.uz) больше не живут в этом репозитории.
Новый проект — `~/projects/portfolio`: backend переписан на
[django-template](https://github.com/igorkhaylov/django-template)
(Django 5.2, DRF, PostgreSQL, Redis, Celery, MinIO, Docker), фронтенд — прежний
iPortfolio, но весь текст теперь берётся из базы, а не из шаблонов.

Документация нового проекта: `README.md` и `docs/content.md` внутри `portfolio`.

## Что осталось здесь

Этот репозиторий называется так же, как GitHub-аккаунт, поэтому его `README.md`
рендерится на странице профиля. Всё остальное ему не нужно.

Старые исходники сайта (Django 4.0) остаются в истории git — если понадобятся, они
доступны по любому коммиту до переноса:

```bash
git log --oneline -- main/          # найти нужный коммит
git show <commit>:main/models.py    # посмотреть файл
```

Удалить их из рабочего дерева и из индекса:

```bash
git rm -r igorkhaylov main templates static locale manage.py requirements.txt
rm -rf tmp
git commit -m "[IMP] move the portfolio site out of the profile repository"
```
