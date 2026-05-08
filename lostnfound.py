from __future__ import annotations

import os
import sqlite3
import uuid
from functools import wraps
from typing import Any

from flask import Flask, flash, g, redirect, render_template_string, request, send_file, session, url_for
from jinja2 import DictLoader
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


BASE_DIR = __file__.rsplit("\\", 1)[0] if "\\" in __file__ else "."
DATABASE = f"{BASE_DIR}\\bisu_lostnfound.db"
LOGO_PATH = r"C:\Users\Josephine\Downloads\bisu_logo.png"
UPLOAD_DIR = f"{BASE_DIR}\\uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "bisu-lostnfound-secret-key"


BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        :root {
            --navy: #0f2f57;
            --blue: #1a4f8b;
            --teal: #2f7a86;
            --sand: #f5efe5;
            --gold: #d7a423;
            --ink: #1b2733;
            --muted: #607180;
            --panel: rgba(255, 255, 255, 0.86);
            --line: rgba(15, 47, 87, 0.12);
            --ok: #1f7a4d;
            --warn: #9a6a10;
            --bad: #a33a3a;
            --shadow: 0 30px 70px rgba(15, 47, 87, 0.14);
            --radius-lg: 30px;
            --radius-md: 18px;
            --radius-sm: 12px;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            color: var(--ink);
            background:
                radial-gradient(circle at top left, rgba(215, 164, 35, 0.22), transparent 24%),
                radial-gradient(circle at 85% 10%, rgba(26, 79, 139, 0.18), transparent 20%),
                linear-gradient(145deg, #f6efe4 0%, #f7f9fc 44%, #edf4fb 100%);
            min-height: 100vh;
        }

        body::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background:
                linear-gradient(rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.08)),
                repeating-linear-gradient(
                    90deg,
                    transparent 0,
                    transparent 78px,
                    rgba(15, 47, 87, 0.025) 79px,
                    rgba(15, 47, 87, 0.025) 80px
                );
            opacity: 0.45;
        }

        a {
            color: inherit;
            text-decoration: none;
        }

        .shell {
            width: min(1240px, calc(100% - 32px));
            margin: 0 auto;
            padding: 28px 0 48px;
        }

        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
            margin-bottom: 28px;
            padding: 18px 22px;
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.72);
            box-shadow: 0 16px 42px rgba(15, 47, 87, 0.08);
            backdrop-filter: blur(18px);
            position: sticky;
            top: 16px;
            z-index: 5;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .brand-mark {
            width: 60px;
            height: 60px;
            border-radius: 18px;
            overflow: hidden;
            flex: 0 0 auto;
            background: linear-gradient(160deg, rgba(15, 47, 87, 0.08), rgba(47, 122, 134, 0.08));
            border: 1px solid rgba(15, 47, 87, 0.08);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
        }

        .brand-mark img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        .brand-copy h1,
        .brand-copy p {
            margin: 0;
        }

        .brand-copy h1 {
            font-size: 1.02rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .brand-copy p {
            color: var(--muted);
            font-size: 0.92rem;
        }

        .nav-links {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: flex-end;
            gap: 10px;
        }

        .nav-links a,
        .nav-links button {
            border: 0;
            cursor: pointer;
            padding: 11px 16px;
            border-radius: 999px;
            background: transparent;
            color: var(--navy);
            font-weight: 600;
        }

        .nav-links .accent,
        .button {
            background: linear-gradient(135deg, var(--navy), var(--blue));
            color: white;
            box-shadow: 0 14px 30px rgba(15, 47, 87, 0.18);
        }

        .hero {
            display: block;
            margin-bottom: 24px;
        }

        .card {
            background: var(--panel);
            border: 1px solid rgba(255, 255, 255, 0.68);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow);
            backdrop-filter: blur(18px);
        }

        .hero-main,
        .hero-side,
        .section,
        .auth-card {
            padding: 28px;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(216, 168, 63, 0.16);
            color: var(--navy);
            font-size: 0.82rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            font-weight: 700;
        }

        .hero h2,
        .section h3,
        .auth-card h2 {
            margin: 16px 0 10px;
            line-height: 1.1;
        }

        .hero h2 {
            font-size: clamp(2.3rem, 4vw, 4.3rem);
            max-width: 12ch;
        }

        .hero-main {
            position: relative;
            overflow: hidden;
            width: 100%;
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(245, 249, 255, 0.88)),
                radial-gradient(circle at top right, rgba(215, 164, 35, 0.18), transparent 26%);
        }

        .hero-main::after {
            content: "";
            position: absolute;
            right: -60px;
            top: -80px;
            width: 240px;
            height: 240px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(26, 79, 139, 0.16), transparent 68%);
        }

        .hero-side {
            position: relative;
            overflow: hidden;
            color: white;
            background:
                linear-gradient(180deg, rgba(10, 34, 68, 0.84), rgba(23, 76, 128, 0.92)),
                linear-gradient(135deg, var(--navy), var(--blue));
        }

        .hero-side h2,
        .hero-side p,
        .hero-side .hint {
            color: rgba(255, 255, 255, 0.9);
        }

        .lead,
        .section p,
        .auth-card p {
            color: var(--muted);
            line-height: 1.65;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-top: 22px;
        }

        .stat {
            padding: 18px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid var(--line);
            border-top-width: 4px;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
        }

        .stat strong {
            display: block;
            font-size: 1.5rem;
            color: var(--navy);
        }

        .stat span {
            color: var(--muted);
            font-size: 0.9rem;
        }

        .stat.pending-stat {
            background: linear-gradient(180deg, rgba(255, 248, 230, 0.96), rgba(255, 255, 255, 0.82));
            border-color: rgba(215, 164, 35, 0.2);
            border-top-color: var(--gold);
        }

        .stat.pending-stat strong {
            color: #9a6a10;
        }

        .stat.approved-stat {
            background: linear-gradient(180deg, rgba(233, 249, 240, 0.96), rgba(255, 255, 255, 0.82));
            border-color: rgba(31, 122, 77, 0.18);
            border-top-color: var(--ok);
        }

        .stat.approved-stat strong {
            color: var(--ok);
        }

        .stat.found-stat {
            background: linear-gradient(180deg, rgba(234, 243, 255, 0.96), rgba(255, 255, 255, 0.82));
            border-color: rgba(26, 79, 139, 0.18);
            border-top-color: var(--blue);
        }

        .stat.found-stat strong {
            color: var(--blue);
        }

        .stat.rejected-stat {
            background: linear-gradient(180deg, rgba(253, 237, 237, 0.96), rgba(255, 255, 255, 0.82));
            border-color: rgba(163, 58, 58, 0.18);
            border-top-color: var(--bad);
        }

        .stat.rejected-stat strong {
            color: var(--bad);
        }

        .grid {
            display: grid;
            grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
            gap: 22px;
            align-items: start;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-top: 18px;
            padding: 10px 14px;
            border-radius: 999px;
            background: rgba(15, 47, 87, 0.06);
            color: var(--navy);
            font-size: 0.92rem;
            font-weight: 600;
        }

        .hero-badge img {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            object-fit: cover;
        }

        .campus-panel {
            margin-top: 20px;
            padding: 18px;
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.14);
        }

        .campus-panel strong,
        .campus-panel span {
            display: block;
        }

        .campus-panel strong {
            font-size: 1.15rem;
            margin-bottom: 6px;
        }

        .campus-panel span {
            color: rgba(255, 255, 255, 0.76);
            line-height: 1.6;
        }

        form {
            display: grid;
            gap: 14px;
        }

        .field-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
        }

        label {
            display: grid;
            gap: 8px;
            font-size: 0.94rem;
            font-weight: 600;
            color: var(--navy);
        }

        input,
        select,
        textarea {
            width: 100%;
            border: 1px solid rgba(16, 61, 95, 0.14);
            background: rgba(255, 255, 255, 0.82);
            border-radius: var(--radius-sm);
            padding: 13px 14px;
            font: inherit;
            color: var(--ink);
            outline: none;
        }

        input:focus,
        select:focus,
        textarea:focus {
            border-color: rgba(31, 122, 140, 0.7);
            box-shadow: 0 0 0 4px rgba(31, 122, 140, 0.12);
        }

        textarea {
            min-height: 120px;
            resize: vertical;
        }

        .button,
        .ghost-button,
        .mini-button {
            border: 0;
            cursor: pointer;
            font: inherit;
            font-weight: 700;
        }

        .button,
        .ghost-button {
            padding: 13px 16px;
            border-radius: 14px;
        }

        .ghost-button {
            background: rgba(16, 61, 95, 0.06);
            color: var(--navy);
        }

        .post-trigger {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 150px;
        }

        .section-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 8px;
        }

        .section-head h3 {
            margin-bottom: 0;
        }

        .minimize-button {
            padding: 10px 14px;
            border-radius: 999px;
            border: 1px solid rgba(15, 47, 87, 0.12);
            background: rgba(15, 47, 87, 0.06);
            color: var(--navy);
            font: inherit;
            font-weight: 700;
            cursor: pointer;
        }

        .mini-button {
            padding: 10px 14px;
            border-radius: 999px;
            color: white;
        }

        .approve {
            background: var(--ok);
        }

        .reject {
            background: var(--bad);
        }

        .delete {
            background: #475569;
        }

        .status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.82rem;
            text-transform: capitalize;
        }

        .status.pending {
            color: var(--warn);
            background: rgba(216, 168, 63, 0.15);
        }

        .status.approved {
            color: var(--ok);
            background: rgba(31, 122, 77, 0.12);
        }

        .status.rejected {
            color: var(--bad);
            background: rgba(163, 58, 58, 0.12);
        }

        .items {
            display: grid;
            gap: 14px;
        }

        .queue-shell {
            margin-top: 18px;
            padding: 18px;
            border-radius: 24px;
            background:
                linear-gradient(180deg, rgba(248, 251, 255, 0.95), rgba(238, 246, 255, 0.9)),
                rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(26, 79, 139, 0.12);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
        }

        .queue-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 14px;
        }

        .queue-head p {
            margin: 6px 0 0;
            max-width: 44ch;
            font-size: 0.94rem;
        }

        .queue-count {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 78px;
            padding: 12px 16px;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(15, 47, 87, 0.96), rgba(26, 79, 139, 0.9));
            color: white;
            box-shadow: 0 16px 32px rgba(15, 47, 87, 0.18);
        }

        .queue-count strong {
            display: block;
            font-size: 1.15rem;
            line-height: 1;
        }

        .queue-count span {
            display: block;
            margin-top: 4px;
            font-size: 0.74rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.76;
        }

        .queue-scroll {
            max-height: 520px;
            overflow-y: auto;
            padding-right: 8px;
        }

        .reviewed-scroll {
            max-height: 420px;
            overflow-y: auto;
            padding-right: 8px;
        }

        .reviewed-scroll::-webkit-scrollbar {
            width: 10px;
        }

        .reviewed-scroll::-webkit-scrollbar-track {
            background: rgba(15, 47, 87, 0.06);
            border-radius: 999px;
        }

        .reviewed-scroll::-webkit-scrollbar-thumb {
            background: rgba(26, 79, 139, 0.28);
            border-radius: 999px;
        }

        .reviewed-scroll::-webkit-scrollbar-thumb:hover {
            background: rgba(26, 79, 139, 0.42);
        }

        .queue-scroll::-webkit-scrollbar {
            width: 10px;
        }

        .queue-scroll::-webkit-scrollbar-track {
            background: rgba(15, 47, 87, 0.06);
            border-radius: 999px;
        }

        .queue-scroll::-webkit-scrollbar-thumb {
            background: rgba(26, 79, 139, 0.34);
            border-radius: 999px;
        }

        .queue-scroll::-webkit-scrollbar-thumb:hover {
            background: rgba(26, 79, 139, 0.5);
        }

        .item {
            padding: 18px;
            border-radius: 20px;
            border: 1px solid var(--line);
            background: rgba(255, 255, 255, 0.74);
            box-shadow: 0 12px 26px rgba(15, 47, 87, 0.06);
        }

        .queue-shell .item {
            padding: 20px;
            border-radius: 22px;
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(244, 249, 255, 0.92)),
                rgba(255, 255, 255, 0.92);
            border-color: rgba(15, 47, 87, 0.08);
            box-shadow:
                0 18px 34px rgba(15, 47, 87, 0.08),
                inset 0 1px 0 rgba(255, 255, 255, 0.88);
        }

        .item-photo {
            width: 100%;
            max-height: 260px;
            object-fit: cover;
            border-radius: 18px;
            margin-top: 14px;
            border: 1px solid rgba(15, 47, 87, 0.08);
            background: #edf2f7;
        }

        .compact-section {
            padding: 22px;
        }

        .compact-section h3 {
            margin-top: 12px;
            margin-bottom: 6px;
        }

        .compact-section > p {
            margin-top: 0;
            margin-bottom: 14px;
        }

        .compact-section .items {
            gap: 12px;
        }

        .approved-scroll {
            max-height: 720px;
            overflow-y: auto;
            padding-right: 6px;
        }

        .approved-scroll::-webkit-scrollbar {
            width: 10px;
        }

        .approved-scroll::-webkit-scrollbar-track {
            background: rgba(15, 47, 87, 0.06);
            border-radius: 999px;
        }

        .approved-scroll::-webkit-scrollbar-thumb {
            background: rgba(26, 79, 139, 0.28);
            border-radius: 999px;
        }

        .approved-scroll::-webkit-scrollbar-thumb:hover {
            background: rgba(26, 79, 139, 0.42);
        }

        .compact-section .item {
            padding: 14px;
            border-radius: 16px;
        }

        .compact-section .item h4 {
            font-size: 1rem;
        }

        .compact-section .item p {
            margin-top: 8px;
            font-size: 0.94rem;
        }

        .compact-section .item-meta {
            font-size: 0.86rem;
        }

        .compact-section .item-photo {
            max-height: 180px;
            border-radius: 14px;
        }

        .item-top,
        .item-meta,
        .action-row,
        .flash {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
        }

        .item-top {
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .item h4,
        .item p {
            margin: 0;
        }

        .item h4 {
            font-size: 1.1rem;
        }

        .item-meta,
        .hint,
        .empty {
            color: var(--muted);
            font-size: 0.92rem;
        }

        .item p {
            margin-top: 10px;
            line-height: 1.6;
        }

        .queue-shell .item p {
            color: #415468;
        }

        .flash-wrap {
            display: grid;
            gap: 10px;
            margin-bottom: 18px;
        }

        .flash {
            justify-content: space-between;
            padding: 14px 16px;
            border-radius: 16px;
            border: 1px solid;
        }

        .flash.success {
            background: rgba(31, 122, 77, 0.1);
            border-color: rgba(31, 122, 77, 0.2);
            color: var(--ok);
        }

        .flash.error {
            background: rgba(163, 58, 58, 0.1);
            border-color: rgba(163, 58, 58, 0.18);
            color: var(--bad);
        }

        .flash.info {
            background: rgba(16, 61, 95, 0.08);
            border-color: rgba(16, 61, 95, 0.12);
            color: var(--navy);
        }

        .auth-wrap {
            width: min(560px, calc(100% - 16px));
            margin: 50px auto;
        }

        .submission-card {
            display: none;
            margin-top: 18px;
        }

        .submission-card.is-open {
            display: block;
        }

        .auth-card {
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(248, 251, 255, 0.9)),
                rgba(255, 255, 255, 0.88);
        }

        .auth-logo {
            width: 88px;
            height: 88px;
            margin-bottom: 12px;
            border-radius: 24px;
            object-fit: cover;
            box-shadow: 0 12px 28px rgba(15, 47, 87, 0.12);
        }

        .footer-note {
            margin-top: 28px;
            text-align: center;
            color: var(--muted);
            font-size: 0.9rem;
        }

        @media (max-width: 900px) {
            .hero,
            .grid,
            .field-grid,
            .stats {
                grid-template-columns: 1fr;
            }

            .shell {
                width: min(100%, calc(100% - 20px));
            }

            .nav {
                border-radius: 28px;
                padding: 18px;
                position: static;
            }

            .nav,
            .brand,
            .nav-links {
                align-items: flex-start;
                flex-direction: column;
            }

            .nav-links {
                width: 100%;
                justify-content: flex-start;
            }

            .queue-head {
                align-items: flex-start;
                flex-direction: column;
            }

            .queue-count {
                min-width: 0;
            }

            .queue-scroll {
                max-height: 560px;
                padding-right: 2px;
            }
        }
    </style>
</head>
<body>
    {% block body %}{% endblock %}
    <script>
        document.addEventListener("DOMContentLoaded", function () {
            const trigger = document.querySelector("[data-open-post-form]");
            const panel = document.querySelector("[data-post-form-panel]");
            const minimize = document.querySelector("[data-close-post-form]");

            if (!trigger || !panel) {
                return;
            }

            trigger.addEventListener("click", function () {
                panel.classList.add("is-open");
                trigger.style.display = "none";
                const firstInput = panel.querySelector("input, select, textarea");
                if (firstInput) {
                    firstInput.focus();
                }
            });

            if (minimize) {
                minimize.addEventListener("click", function () {
                    panel.classList.remove("is-open");
                    trigger.style.display = "inline-flex";
                });
            }
        });
    </script>
</body>
</html>
"""


HOME_HTML = """
{% extends base %}
{% block body %}
<div class="shell">
    <div class="nav">
        <div class="brand">
            <div class="brand-mark"><img src="{{ url_for('bisu_logo') }}" alt="BISU logo"></div>
            <div class="brand-copy">
                <h1>BISU CALAPE Lost & Found</h1>
                <p>Campus item reporting with admin moderation.</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="{{ url_for('home') }}">Home</a>
            <a href="{{ url_for('admin_login') }}">Admin Login</a>
            <a href="{{ url_for('admin_register') }}" class="accent">Admin Register</a>
        </div>
    </div>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="flash-wrap">
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <div class="hero">
        <section class="card hero-main">
            <span class="eyebrow">BISU CALAPE Lost & Found</span>
            <h2>Helping the BISU Calape community recover lost items faster.</h2>
            <div class="hero-badge">
                <img src="{{ url_for('bisu_logo') }}" alt="BISU seal">
                <span>Official BISU Calape community lost and found board</span>
            </div>
            <div class="stats">
                <div class="stat pending-stat">
                    <strong>{{ counts.pending }}</strong>
                    <span>Pending Review</span>
                </div>
                <div class="stat approved-stat">
                    <strong>{{ counts.approved }}</strong>
                    <span>Approved Posts</span>
                </div>
                <div class="stat found-stat">
                    <strong>{{ counts.found }}</strong>
                    <span>Found Item Reports</span>
                </div>
            </div>
        </section>
    </div>

    <div class="grid">
        <section class="card section">
            <span class="eyebrow">Public Submission</span>
            <button type="button" class="button post-trigger" data-open-post-form>Post</button>
            <div class="submission-card" data-post-form-panel>
                <div class="section-head">
                    <h3>Create a lost or found post</h3>
                    <button type="button" class="minimize-button" data-close-post-form>Minimize</button>
                </div>
                <p>Fill in the details clearly so BISU admins can review the submission quickly.</p>
                <form method="post" action="{{ url_for('submit_post') }}" enctype="multipart/form-data">
                    <div class="field-grid">
                        <label>
                            Your name
                            <input type="text" name="reporter_name" required>
                        </label>
                        <label>
                            Contact information
                            <input type="text" name="contact_info" placeholder="Email, phone, or Facebook" required>
                        </label>
                    </div>
                    <div class="field-grid">
                        <label>
                            Post type
                            <select name="post_type" required>
                                <option value="lost">Lost Item</option>
                                <option value="found">Found Item</option>
                            </select>
                        </label>
                        <label>
                            Item name
                            <input type="text" name="item_name" placeholder="Wallet, ID, phone, bag..." required>
                        </label>
                    </div>
                    <div class="field-grid">
                        <label>
                            Item category
                            <input type="text" name="item_category" placeholder="Electronics, documents, accessories">
                        </label>
                        <label>
                            Date seen
                            <input type="date" name="date_seen" required>
                        </label>
                    </div>
                    <label>
                        Last known or found location
                        <input type="text" name="location" placeholder="Campus building, room, gate, or area" required>
                    </label>
                    <label>
                        Item details
                        <textarea name="description" placeholder="Describe color, brand, markings, or identifying details" required></textarea>
                    </label>
                    <label>
                        Item photo
                        <input type="file" name="item_photo" accept=".png,.jpg,.jpeg,.gif,.webp,image/*">
                    </label>
                    <button type="submit" class="button">Submit for admin review</button>
                </form>
            </div>
        </section>

        <section class="card section compact-section">
            <span class="eyebrow">Approved Posts</span>
            <h3>Visible to the BISU Calape community</h3>
            <p>These reports have already been reviewed and approved by an admin.</p>
            <div class="items approved-scroll">
                {% for post in approved_posts %}
                    <article class="item">
                        <div class="item-top">
                            <div>
                                <h4>{{ post["item_name"] }}</h4>
                                <div class="item-meta">
                                    <span>{{ post["post_type"].title() }}</span>
                                    <span>•</span>
                                    <span>{{ post["item_category"] or "General Item" }}</span>
                                </div>
                            </div>
                            <span class="status approved">{{ post["status"] }}</span>
                        </div>
                        <div class="item-meta">
                            <span>{{ post["location"] }}</span>
                            <span>•</span>
                            <span>{{ post["date_seen"] }}</span>
                            <span>•</span>
                            <span>Contact: {{ post["contact_info"] }}</span>
                        </div>
                        <p>{{ post["description"] }}</p>
                        {% if post["photo_filename"] %}
                            <img class="item-photo" src="{{ url_for('uploaded_photo', filename=post['photo_filename']) }}" alt="Photo of {{ post['item_name'] }}">
                        {% endif %}
                    </article>
                {% else %}
                    <div class="empty">No approved posts yet. Submitted items will appear here after admin approval.</div>
                {% endfor %}
            </div>
        </section>
    </div>

    <p class="footer-note">BISU CALAPE Lost & Found system with public posting and admin moderation.</p>
</div>
{% endblock %}
"""


DASHBOARD_HTML = """
{% extends base %}
{% block body %}
<div class="shell">
    <div class="nav">
        <div class="brand">
            <div class="brand-mark"><img src="{{ url_for('bisu_logo') }}" alt="BISU logo"></div>
            <div class="brand-copy">
                <h1>BISU CALAPE Lost & Found</h1>
                <p>Admin dashboard and moderation queue.</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="{{ url_for('home') }}">Public Page</a>
            <form method="post" action="{{ url_for('admin_logout') }}">
                <button type="submit" class="accent">Logout</button>
            </form>
        </div>
    </div>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="flash-wrap">
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <div class="hero">
        <section class="card hero-main">
            <span class="eyebrow">BISU CALAPE</span>
            <h2>BISU CALAPE Lost & Found</h2>
            <div class="hero-badge">
                <img src="{{ url_for('bisu_logo') }}" alt="BISU seal">
                <span>Official BISU Calape community lost and found board</span>
            </div>
            <div class="stats">
                <div class="stat pending-stat">
                    <strong>{{ counts.pending }}</strong>
                    <span>Pending Review</span>
                </div>
                <div class="stat approved-stat">
                    <strong>{{ counts.approved }}</strong>
                    <span>Approved Posts</span>
                </div>
                <div class="stat found-stat">
                    <strong>{{ counts.found }}</strong>
                    <span>Found Item Reports</span>
                </div>
            </div>
        </section>
    </div>

    <div class="grid">
        <section class="card section">
            <span class="eyebrow">Pending Queue</span>
            <h3>Posts waiting for review</h3>
            <div class="queue-shell">
                <div class="queue-head">
                    <div>
                        <strong>Moderation queue</strong>
                        <p>Newest submissions stay neatly inside this review panel so the dashboard remains compact and easier to scan.</p>
                    </div>
                    <div class="queue-count">
                        <div>
                            <strong>{{ pending_posts|length }}</strong>
                            <span>In Queue</span>
                        </div>
                    </div>
                </div>
                <div class="queue-scroll">
                    <div class="items">
                        {% for post in pending_posts %}
                            <article class="item">
                                <div class="item-top">
                                    <div>
                                        <h4>{{ post["item_name"] }}</h4>
                                        <div class="item-meta">
                                            <span>{{ post["post_type"].title() }}</span>
                                            <span>•</span>
                                            <span>{{ post["item_category"] or "General Item" }}</span>
                                        </div>
                                    </div>
                                    <span class="status pending">{{ post["status"] }}</span>
                                </div>
                                <div class="item-meta">
                                    <span>By {{ post["reporter_name"] }}</span>
                                    <span>•</span>
                                    <span>{{ post["contact_info"] }}</span>
                                    <span>•</span>
                                    <span>{{ post["location"] }}</span>
                                    <span>•</span>
                                    <span>{{ post["date_seen"] }}</span>
                                </div>
                                <p>{{ post["description"] }}</p>
                                {% if post["photo_filename"] %}
                                    <img class="item-photo" src="{{ url_for('uploaded_photo', filename=post['photo_filename']) }}" alt="Photo of {{ post['item_name'] }}">
                                {% endif %}
                                <div class="action-row">
                                    <form method="post" action="{{ url_for('update_status', post_id=post['id'], new_status='approved') }}">
                                        <button type="submit" class="mini-button approve">Approve</button>
                                    </form>
                                    <form method="post" action="{{ url_for('update_status', post_id=post['id'], new_status='rejected') }}">
                                        <button type="submit" class="mini-button reject">Reject</button>
                                    </form>
                                </div>
                            </article>
                        {% else %}
                            <div class="empty">No pending posts right now.</div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </section>

        <section class="card section">
            <span class="eyebrow">Recent Decisions</span>
            <h3>Approved and rejected posts</h3>
            <div class="items reviewed-scroll">
                {% for post in reviewed_posts %}
                    <article class="item">
                        <div class="item-top">
                            <div>
                                <h4>{{ post["item_name"] }}</h4>
                                <div class="item-meta">
                                    <span>{{ post["post_type"].title() }}</span>
                                    <span>•</span>
                                    <span>{{ post["location"] }}</span>
                                </div>
                            </div>
                            <span class="status {{ post['status'] }}">{{ post["status"] }}</span>
                        </div>
                        <div class="item-meta">
                            <span>{{ post["date_seen"] }}</span>
                            <span>•</span>
                            <span>{{ post["reporter_name"] }}</span>
                        </div>
                        <p>{{ post["description"] }}</p>
                        {% if post["photo_filename"] %}
                            <img class="item-photo" src="{{ url_for('uploaded_photo', filename=post['photo_filename']) }}" alt="Photo of {{ post['item_name'] }}">
                        {% endif %}
                        {% if post["status"] == "approved" %}
                            <div class="action-row">
                                <form method="post" action="{{ url_for('delete_post', post_id=post['id']) }}">
                                    <button type="submit" class="mini-button delete">Delete Resolved Post</button>
                                </form>
                            </div>
                        {% endif %}
                    </article>
                {% else %}
                    <div class="empty">No reviewed posts yet.</div>
                {% endfor %}
            </div>
        </section>
    </div>
</div>
{% endblock %}
"""


AUTH_HTML = """
{% extends base %}
{% block body %}
<div class="shell">
    <div class="nav">
        <div class="brand">
            <div class="brand-mark"><img src="{{ url_for('bisu_logo') }}" alt="BISU logo"></div>
            <div class="brand-copy">
                <h1>BISU CALAPE Lost & Found</h1>
                <p>Admin-only access for moderation.</p>
            </div>
        </div>
        <div class="nav-links">
            <a href="{{ url_for('home') }}">Public Page</a>
            <a href="{{ url_for('admin_login') }}">Login</a>
            <a href="{{ url_for('admin_register') }}" class="accent">Register</a>
        </div>
    </div>

    <div class="auth-wrap">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flash-wrap">
                    {% for category, message in messages %}
                        <div class="flash {{ category }}">{{ message }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        <section class="card auth-card">
            <img class="auth-logo" src="{{ url_for('bisu_logo') }}" alt="BISU seal">
            <span class="eyebrow">{{ eyebrow }}</span>
            <h2>{{ heading }}</h2>
            <p>{{ subtext }}</p>
            <form method="post">
                {% if mode == 'register' %}
                    <label>
                        Admin full name
                        <input type="text" name="full_name" required>
                    </label>
                {% endif %}
                <label>
                    Username
                    <input type="text" name="username" required>
                </label>
                <label>
                    Password
                    <input type="password" name="password" required>
                </label>
                <button type="submit" class="button">{{ button_text }}</button>
            </form>
        </section>
    </div>
</div>
{% endblock %}
"""


app.jinja_loader = DictLoader(
    {
        "base.html": BASE_HTML,
        "home.html": HOME_HTML,
        "dashboard.html": DASHBOARD_HTML,
        "auth.html": AUTH_HTML,
    }
)


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_: Any) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_name TEXT NOT NULL,
            contact_info TEXT NOT NULL,
            post_type TEXT NOT NULL,
            item_name TEXT NOT NULL,
            item_category TEXT,
            location TEXT NOT NULL,
            date_seen TEXT NOT NULL,
            description TEXT NOT NULL,
            photo_filename TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(posts)").fetchall()}
    if "photo_filename" not in columns:
        cursor.execute("ALTER TABLE posts ADD COLUMN photo_filename TEXT")
    db.commit()
    db.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "admin_id" not in session:
            flash("Please log in as admin to continue.", "error")
            return redirect(url_for("admin_login"))
        return view(**kwargs)

    return wrapped_view


def query_all(query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    return get_db().execute(query, params).fetchall()


def query_one(query: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    return get_db().execute(query, params).fetchone()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_photo() -> str | None:
    file = request.files.get("item_photo")
    if file is None or not file.filename:
        return None

    if not allowed_file(file.filename):
        raise ValueError("Please upload a valid image file: PNG, JPG, JPEG, GIF, or WEBP.")

    original_name = secure_filename(file.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    file.save(os.path.join(UPLOAD_DIR, filename))
    return filename


def delete_photo_file(filename: str | None) -> None:
    if not filename:
        return

    safe_name = secure_filename(filename)
    photo_path = os.path.join(UPLOAD_DIR, safe_name)
    if os.path.exists(photo_path):
        os.remove(photo_path)


def get_counts() -> dict[str, int]:
    rows = query_all("SELECT status, COUNT(*) AS total FROM posts GROUP BY status")
    counts = {"pending": 0, "approved": 0, "rejected": 0, "found": 0}
    for row in rows:
        counts[row["status"]] = row["total"]
    found_row = query_one("SELECT COUNT(*) AS total FROM posts WHERE post_type = 'found'")
    counts["found"] = found_row["total"] if found_row else 0
    return counts


def render_page(template: str, **context: Any) -> str:
    return render_template_string(template, base="base.html", **context)


@app.before_request
def ensure_database() -> None:
    init_db()


@app.route("/bisu-logo")
def bisu_logo() -> Any:
    return send_file(LOGO_PATH, mimetype="image/png")


@app.route("/uploads/<filename>")
def uploaded_photo(filename: str) -> Any:
    safe_name = secure_filename(filename)
    return send_file(os.path.join(UPLOAD_DIR, safe_name))


@app.route("/")
def home() -> str:
    approved_posts = query_all(
        "SELECT * FROM posts WHERE status = 'approved' ORDER BY created_at DESC, id DESC"
    )
    return render_page(
        HOME_HTML,
        title="BISU CALAPE Lost & Found",
        approved_posts=approved_posts,
        counts=get_counts(),
    )


@app.post("/submit")
def submit_post() -> Any:
    reporter_name = request.form.get("reporter_name", "").strip()
    contact_info = request.form.get("contact_info", "").strip()
    post_type = request.form.get("post_type", "").strip().lower()
    item_name = request.form.get("item_name", "").strip()
    item_category = request.form.get("item_category", "").strip()
    location = request.form.get("location", "").strip()
    date_seen = request.form.get("date_seen", "").strip()
    description = request.form.get("description", "").strip()
    photo_filename = None

    if not all([reporter_name, contact_info, post_type, item_name, location, date_seen, description]):
        flash("Please fill in all required item details.", "error")
        return redirect(url_for("home"))

    if post_type not in {"lost", "found"}:
        flash("Invalid post type selected.", "error")
        return redirect(url_for("home"))

    try:
        photo_filename = save_uploaded_photo()
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("home"))

    db = get_db()
    db.execute(
        """
        INSERT INTO posts (
            reporter_name, contact_info, post_type, item_name, item_category,
            location, date_seen, description, photo_filename, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """,
        (
            reporter_name,
            contact_info,
            post_type,
            item_name,
            item_category,
            location,
            date_seen,
            description,
            photo_filename,
        ),
    )
    db.commit()
    flash("Your post was submitted and is now waiting for admin approval.", "success")
    return redirect(url_for("home"))


@app.route("/admin/register", methods=["GET", "POST"])
def admin_register() -> Any:
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not all([full_name, username, password]):
            flash("Please complete the admin registration form.", "error")
            return redirect(url_for("admin_register"))

        if query_one("SELECT id FROM admins WHERE username = ?", (username,)):
            flash("That admin username is already registered.", "error")
            return redirect(url_for("admin_register"))

        db = get_db()
        db.execute(
            "INSERT INTO admins (full_name, username, password_hash) VALUES (?, ?, ?)",
            (full_name, username, generate_password_hash(password)),
        )
        db.commit()
        flash("Admin account created successfully. You can now log in.", "success")
        return redirect(url_for("admin_login"))

    return render_page(
        AUTH_HTML,
        title="Admin Register | BISU CALAPE Lost & Found",
        eyebrow="Admin Register",
        heading="Create an admin account",
        subtext="Only admins can log in and approve or reject user submissions.",
        button_text="Register Admin",
        mode="register",
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login() -> Any:
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        admin = query_one("SELECT * FROM admins WHERE username = ?", (username,))

        if admin is None or not check_password_hash(admin["password_hash"], password):
            flash("Invalid admin username or password.", "error")
            return redirect(url_for("admin_login"))

        session.clear()
        session["admin_id"] = admin["id"]
        session["admin_name"] = admin["full_name"]
        flash("Welcome back. Admin login successful.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_page(
        AUTH_HTML,
        title="Admin Login | BISU CALAPE Lost & Found",
        eyebrow="Admin Login",
        heading="Log in to the dashboard",
        subtext="Review public submissions and decide which posts go live.",
        button_text="Log In",
        mode="login",
    )


@app.post("/admin/logout")
def admin_logout() -> Any:
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/admin/dashboard")
@login_required
def admin_dashboard() -> str:
    pending_posts = query_all(
        "SELECT * FROM posts WHERE status = 'pending' ORDER BY created_at ASC, id ASC LIMIT 20"
    )
    reviewed_posts = query_all(
        "SELECT * FROM posts WHERE status != 'pending' ORDER BY created_at DESC, id DESC LIMIT 8"
    )
    return render_page(
        DASHBOARD_HTML,
        title="Admin Dashboard | BISU CALAPE Lost & Found",
        pending_posts=pending_posts,
        reviewed_posts=reviewed_posts,
        counts=get_counts(),
        admin_name=session.get("admin_name", "Admin"),
    )


@app.post("/admin/posts/<int:post_id>/<new_status>")
@login_required
def update_status(post_id: int, new_status: str) -> Any:
    if new_status not in {"approved", "rejected"}:
        flash("Invalid moderation action.", "error")
        return redirect(url_for("admin_dashboard"))

    db = get_db()
    updated = db.execute(
        "UPDATE posts SET status = ? WHERE id = ?",
        (new_status, post_id),
    )
    db.commit()

    if updated.rowcount == 0:
        flash("Post not found.", "error")
    else:
        flash(f"Post {new_status} successfully.", "success")

    return redirect(url_for("admin_dashboard"))


@app.post("/admin/posts/<int:post_id>/delete")
@login_required
def delete_post(post_id: int) -> Any:
    post = query_one("SELECT id, post_type, item_name, photo_filename FROM posts WHERE id = ?", (post_id,))
    if post is None:
        flash("Post not found.", "error")
        return redirect(url_for("admin_dashboard"))

    db = get_db()
    db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db.commit()
    delete_photo_file(post["photo_filename"])
    if post["post_type"] == "lost":
        flash(f'Notification: "{post["item_name"]}" was removed because the lost item was found.', "success")
    else:
        flash(f'Notification: "{post["item_name"]}" was removed because the found item was returned.', "success")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
