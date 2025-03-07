# NxGen Website

A modern Django web application with user authentication, profile management, and a responsive UI.

## Technology Stack

- Python 3.8+
- Django 4.2+
- Bootstrap 5
- SQLite (development)
- Pillow (for image handling)
- Font Awesome 6 (for icons)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Setup Instructions

1. **Clone the repository**
    ```bash
    git clone https://github.com/nexgenclub/nxgen-website.git
    cd nxgen-website
    ```

2. **Install the required packages**
    ```bash
    pip install -r requirements.txt
    ```

3. **Initialize the database**
    ```bash
    python manage.py migrate
    ```

4. **Run the development server**
    ```bash
    python manage.py runserver
    ```

## Usage

1. Open your web browser and navigate to `http://127.0.0.1:8000/`

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature-branch`)
6. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.