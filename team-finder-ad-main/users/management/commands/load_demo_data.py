from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import Skill, User


class Command(BaseCommand):
    help = "Load demo users, skills, and projects"

    def handle(self, *args, **options):
        skills = {}
        for name in (
            "Python",
            "Django",
            "JavaScript",
            "TypeScript",
            "React",
            "PostgreSQL",
            "Docker",
            "Kubernetes",
            "Git",
            "FastAPI",
            "Redis",
            "CI/CD",
        ):
            skill, _ = Skill.objects.get_or_create(name=name)
            skills[name] = skill

        users_data = [
            {
                "email": "dmitry.volkov@devteam.io",
                "password": "demo12345",
                "name": "Дмитрий",
                "surname": "Волков",
                "phone": "+79161234567",
                "about": "Senior Backend-разработчик с 6-летним опытом. Строю высоконагруженные API на Python и Django.",
                "skill_names": ["Python", "Django", "FastAPI", "PostgreSQL", "Redis"],
            },
            {
                "email": "anastasia.morozova@devteam.io",
                "password": "demo12345",
                "name": "Анастасия",
                "surname": "Морозова",
                "phone": "+79262345678",
                "about": "Frontend-разработчик. Создаю быстрые и удобные интерфейсы на React + TypeScript.",
                "skill_names": ["JavaScript", "TypeScript", "React", "Git"],
            },
            {
                "email": "ivan.sorokin@devteam.io",
                "password": "demo12345",
                "name": "Иван",
                "surname": "Сорокин",
                "phone": "+79037890123",
                "about": "DevOps-инженер. Автоматизирую деплой и настраиваю инфраструктуру для команд любого размера.",
                "skill_names": ["Docker", "Kubernetes", "CI/CD", "Git", "PostgreSQL"],
            },
            {
                "email": "ekaterina.lebedeva@devteam.io",
                "password": "demo12345",
                "name": "Екатерина",
                "surname": "Лебедева",
                "phone": "+79154321098",
                "about": "Fullstack-разработчик. Люблю браться за проекты с нуля и доводить их до продакшена.",
                "skill_names": ["Python", "Django", "React", "PostgreSQL", "Docker"],
            },
            {
                "email": "mikhail.nikitin@devteam.io",
                "password": "demo12345",
                "name": "Михаил",
                "surname": "Никитин",
                "phone": "+79255432109",
                "about": "Разработчик на Python и FastAPI. Интересуюсь ML-инженерией и интеграцией AI в продукты.",
                "skill_names": ["Python", "FastAPI", "Redis", "Docker", "Git"],
            },
        ]

        users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "name": data["name"],
                    "surname": data["surname"],
                    "phone": data["phone"],
                    "about": data["about"],
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
            user.skills.set([skills[name] for name in data["skill_names"]])
            users.append(user)

        projects_data = [
            {
                "name": "DevMatch Platform",
                "description": (
                    "Платформа для поиска соратников по pet-проектам. "
                    "Ищем разработчиков, которые хотят строить реальные продукты вместе."
                ),
                "owner": users[0],
                "github_url": "https://github.com/devteam-io/devmatch",
                "participants": [users[0], users[1], users[2]],
            },
            {
                "name": "OpenMetrics Dashboard",
                "description": (
                    "Дашборд для визуализации метрик микросервисов в реальном времени. "
                    "Prometheus + Grafana под капотом, собственный UI на React."
                ),
                "owner": users[2],
                "github_url": "https://github.com/devteam-io/openmetrics",
                "participants": [users[2], users[3], users[4]],
            },
            {
                "name": "AI Code Reviewer",
                "description": (
                    "Инструмент для автоматического ревью кода с использованием LLM. "
                    "Интегрируется в GitHub Actions и оставляет комментарии к PR."
                ),
                "owner": users[4],
                "github_url": "https://github.com/devteam-io/ai-reviewer",
                "participants": [users[4], users[0]],
            },
            {
                "name": "Fullstack Starter Kit",
                "description": (
                    "Готовый шаблон для быстрого старта проектов: Django REST + React + Docker Compose. "
                    "Включает аутентификацию, CI/CD и примеры тестов."
                ),
                "owner": users[3],
                "participants": [users[3], users[1], users[2]],
            },
        ]

        for data in projects_data:
            project, created = Project.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "owner": data["owner"],
                    "github_url": data.get("github_url", ""),
                },
            )
            if created:
                project.participants.set(data["participants"])
            else:
                for participant in data["participants"]:
                    project.participants.add(participant)

        self.stdout.write(self.style.SUCCESS("Demo data loaded successfully."))
