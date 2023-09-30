# ComfyShop

ComfyShop is an open source project that combines a blog and shop using Django and Wagtail. It provides an easy-to-use interface for managing blog posts and products.

  
[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)](https://www.djangoproject.com/)  


[![Release Version](https://img.shields.io/badge/Release%20Version-v0.2-blue)](https://forge.citizen4.eu/mtyton/comfy/releases/tag/0.2.0)
## Requirements

- Docker
- Docker Compose

## Installation

1. Clone the repository using the following command:  
```git clone https://forge.citizen4.eu/mtyton/comfy.git```
3. Build the Docker image:  
```docker-compose build```
4. Run the Docker container for development:  
```docker-compose up```


For production, use the following command to run the Docker container:  
```docker-compose -f docker-compose-prod.yml up -d```


4. Access the application at [http://127.0.0.1:8001/](http://127.0.0.1:8001/)

## Usage

- Visit the home page to view the blog posts and shop items.

## Customization

- Access the admin panel at [http://127.0.0.1:8001/admin/](http://127.0.0.1:8001/admin/)
- Log in with the superuser credentials (you can create a superuser within the Docker container if not already done).
- Create and manage blog posts and products through the admin panel.

## Contributing

Feel free to contribute to this project by opening issues or creating pull requests. Please follow the contribution guidelines and review the [CONTRIBUTING.md](CONTRIBUTING.md) file for details.

## Documentation

For more detailed information on how to use and customize the application, refer to the [documentation](https://forge.citizen4.eu/mtyton/comfy/wiki).

## License

This project is licensed under the [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.en.html).