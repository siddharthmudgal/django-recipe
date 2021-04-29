# Notes

## important commands
1. Create django project via docker compose
    - ''' docker-compose run --rm app sh -c "django-admin startproject app ." '''
   
2. Run docker
   - ''' docker-compose up '''
   
3. Create super user
   - ''' docker-compose run --rm app sh -c "python manage.py createsuperuser" '''
   
4. Create a new app inside the project
   - ''' docker-compose run --rm app sh -c "python manage.py startapp core" '''
   
5. Run flake8 and tests
   - ''' docker-compose run app sh -c "python manage.py test && flake8" '''