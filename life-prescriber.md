---
date: '2026-01-02'
slug: life-prescriber
title: 'Life Prescriber: A Clinical Prescription Platform'
github: 'https://github.com/olugbeminiyi2000/MedHack_Life_Prescriber'
external: 'https://life-prescriber-322384350452.us-central1.run.app'
tech:
  - Python
  - Django 4.2
  - SQLite
  - GCP Cloud Run
  - Gunicorn
showInProjects: true
---

Life Prescriber connects hospitals and pharmacies through a shared prescription workflow. Hospital clinicians register patients and view drug history in read-only mode through a secured portal. Pharmacists add and manage prescriptions through a separate write-access portal. Each institution gets its own access scope, with head users able to invite staff via time-limited email tokens. Built with Django, deployed on GCP Cloud Run with Gunicorn and WhiteNoise.

**Try it live** — Hospital portal: username `hospital_head` / password `sitdownhere` · Pharmacy portal: username `pharmacy_head` / password `sitdownhere`
