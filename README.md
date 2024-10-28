# Notes Sharing Website

This is an **online notes-sharing platform** built with **Django** and **Tailwind CSS**. It allows users to share, download, and manage notes with an emphasis on accessibility and usability.

## Project Overview

The Notes Sharing Website is designed for students, professionals, and educators to easily share and access notes. It features a responsive design, secure authentication, and user activity tracking. The site is mobile-friendly, modern, and follows best practices for usability and performance.

## Features

- **User Registration & Authentication** (Signup, Login)
- **Notes Upload & Download**
- **Real-time Search** for notes with dynamic filtering
- **User Dashboard** with profile management and activity tracking
- **Responsive Design** using Tailwind CSS
- **Dark Theme (Zinc-900)** with clean, modern visuals
- **Interactive Animations** powered by AOS (Animate on Scroll)

## Technologies Used

- **Backend**: Django
- **Frontend**: Tailwind CSS, HTML5, JavaScript
- **Database**: SQLite (default Django DB)
- **Additional Libraries**: AOS (for animations)

## Project Structure


notes-sharing-website/
│
├── notes_sharing/               # Django project settings
├── notes/                       # Notes app
│   ├── migrations/              # Database migrations
│   ├── templates/               # HTML templates
│   ├── static/                  # Static files (CSS, JavaScript, Images)
│   └── views.py                 # View functions
│
├── media/                       # User-uploaded files (notes)
├── static/                      # Project-wide static assets
├── templates/                   # Project-wide templates
│
├── manage.py                    # Django management file
├── requirements.txt             # Python dependencies
└── README.md                    # Project readme file


