# Публикация проекта на GitHub

Репозиторий уже инициализирован, выполнен первый коммит (ветка `main`).

## Вариант 1: Через веб-интерфейс GitHub

1. Откройте [github.com/new](https://github.com/new).
2. Укажите имя репозитория, например: `labor-estimation` или `labor_estimation`.
3. **Не** добавляйте README, .gitignore и лицензию — они уже есть в проекте.
4. Нажмите **Create repository**.
5. В терминале выполните (подставьте свой логин и имя репозитория):

```bash
cd /Users/sergejbarysnikov/Documents/ed_de_/cost_designer/labor_estimation

git remote add origin https://github.com/YOUR_USERNAME/labor-estimation.git
git push -u origin main
```

При запросе авторизации используйте логин и пароль (или Personal Access Token) GitHub.

## Вариант 2: Через GitHub CLI

Если установлен [GitHub CLI](https://cli.github.com/) (`gh`):

```bash
cd /Users/sergejbarysnikov/Documents/ed_de_/cost_designer/labor_estimation

gh auth login   # если ещё не авторизованы
gh repo create labor-estimation --private --source=. --remote=origin --push
```

Для публичного репозитория замените `--private` на `--public`.

## После публикации

- Репозиторий будет доступен по адресу: `https://github.com/YOUR_USERNAME/labor-estimation`
- Для обновления кода: `git add .` → `git commit -m "описание"` → `git push`
