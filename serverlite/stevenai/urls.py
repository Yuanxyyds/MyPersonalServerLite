"""
URL configuration for landsink app.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    path("gpt4o-qa-docs/query", views.openai_qa_docs, name="openai"),
    path("gpt4o-qa/query", views.openai_qa_only, name="openai"),
    path("gpt4o-docs/query", views.openai_docs_only, name="openai"),
    path("gpt4o/query", views.openai_qa_docs, name="openai"),
    path("llama-qa-docs/query", views.openai_qa_docs, name="openai"),
    path("llama-qa/query", views.openai_qa_docs, name="openai"),
    path("llama-docs/query", views.openai_qa_docs, name="openai"),
    path("llama/query", views.openai_qa_docs, name="openai"),
]
