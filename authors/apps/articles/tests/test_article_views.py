import json
from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.authentication.models import User


class ArticleViewsTestCase(TestCase):
    '''This class implements tests for the article model'''

    def setUp(self):

        # create a user and verify then so they can log in
        self.user1 = User.objects.create_user(
            username='user1', email='user1@mail.com', password='user1user1')
        self.user1.is_verified = True
        self.user1.save()

        self.user2 = User.objects.create_user(
            username='user2', email='user2@mail.com', password='user2user2')
        self.user2.is_verified = True
        self.user2.is_staff = True
        self.user2.save()

        self.user1_credentials = {
            "user": {
                "email": "user1@mail.com",
                "password": "user1user1"
            }
        }
        self.user2_credentials = {
            "user": {
                "email": "user2@mail.com",
                "password": "user2user2"
            }
        }

        self.sample_input = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe",
                "draft": "Giving exellence high priority",
                "tagList": ["dragons", "training"],
 
            }
        }

        self.report_sample = {
            "message":"this article was so biased, it does not respect the muslim culture"
        }

        client = APIClient()

        # Login Users
        user1_login_data = client.post(reverse('authentication:login'),
                                       self.user1_credentials, format='json')
        user2_login_data = client.post(reverse('authentication:login'),
                                       self.user2_credentials, format='json')

        # Get tokens for the 2 users
        token_user1 = user1_login_data.data.get('token')
        token_user2 = user2_login_data.data.get('token')

        # Create login headers for the two users
        self.header_user1 = {
            'HTTP_AUTHORIZATION': f'Bearer {token_user1}'
        }
        self.header_user2 = {
            'HTTP_AUTHORIZATION': f'Bearer {token_user2}'
        }

    def test_create_article_success(self):
        client = APIClient()
        response = client.post(reverse('articles:create_article'),
                               self.sample_input, **self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_get_reading_time(self):
        client = APIClient()
        response = client.post(reverse('articles:create_article'),
                self.sample_input,**self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['Article']['reading_time'], "1 minutes")


    def test_create_article_invalid_data(self):
        sample_input = {
            "article": {
                "description": "Ever wonder how?"
            }
        }
        client = APIClient()
        response = client.post(reverse('articles:create_article'),
                               sample_input, **self.header_user1, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_get_all_articles_not_found(self):
        client = APIClient()
        response = client.get(reverse('articles:get_article'),
                              format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_get_all_articles_success(self):
        # Create article with user1
        client = APIClient()
        respo = client.post(reverse('articles:create_article'),
                            self.sample_input, **self.header_user1, format='json')
        self.assertEqual(respo.status_code, status.HTTP_201_CREATED)

        # Publish article of user1
        my_url = '/api/articles/{}/publish/'.format(respo.data['slug'])
        respo1 = client.patch(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

        # Get all articles
        response = client.get(reverse('articles:get_article'),
                              format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_get_an_article(self):
        client = APIClient()
        respo = client.post(reverse('articles:create_article'),
                            self.sample_input, **self.header_user1, format='json')
        self.assertEqual(respo.status_code, status.HTTP_201_CREATED)

        # Get an article that is not there
        my_url = '/api/articles/{}/'.format(respo.data['slug'])
        respo1 = client.get(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_404_NOT_FOUND)

        # Publish article of user1
        my_url = '/api/articles/{}/publish/'.format(respo.data['slug'])
        respo2 = client.patch(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo2.status_code, status.HTTP_200_OK)

        # Get an article that is there
        my_url = '/api/articles/{}/'.format(respo.data['slug'])
        respo3 = client.get(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo3.status_code, status.HTTP_200_OK)

    def test_update_article_does_not_exist(self):
        # Create article with user1
        client = APIClient()
        respo = client.post(reverse('articles:create_article'),
                            self.sample_input, **self.header_user1, format='json')
        self.assertEqual(respo.status_code, status.HTTP_201_CREATED)

        # Publish article of user1
        my_url = '/api/articles/{}/publish/'.format(respo.data['slug'])
        respo1 = client.patch(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

        # Delete article of user1
        my_url = '/api/articles/{}/edit/'.format(respo.data['slug'])
        respo1 = client.delete(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

        # Try to update the article
        respo1 = client.put(
            my_url,
            self.sample_input,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_article_successfully(self):
        # Create article with user1
        client = APIClient()
        respo = client.post(reverse('articles:create_article'),
                            self.sample_input, **self.header_user1, format='json')
        self.assertEqual(respo.status_code, status.HTTP_201_CREATED)

        # Publish article of user1
        my_url = '/api/articles/{}/publish/'.format(respo.data['slug'])
        respo1 = client.patch(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

        update_input = {
            "article": {
                "title": "I am a champion",
                "description": "In God we trust.",
                "body": "One step infront of the other",
                "draft": "Giving exellence high priority",
                "tagList": ["andela", "The OG"],
                "activated": True
            }
        }

        # Try to update the article with wrong user
        my_url = '/api/articles/{}/edit/'.format(respo.data['slug'])
        respo1 = client.put(
            my_url,
            update_input,
            **self.header_user2,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(respo1.data['detail'],
                         'You are not the owner of the article.')

        # Try to update the article with right user
        respo1 = client.put(
            my_url,
            update_input,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

        #Update without taglist
        update_input = {
            "article": {
                "title": "The PR raisers",
            }
        }
        respo1 = client.put(
            my_url,
            update_input,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)

    def test_publish_article_with_no_draft(self):
        sample_input = {
            "article": {
                "title": "How to train your dragon",
                "description": "Ever wonder how?",
                "body": "You have to believe"
            }
        }
        # Create article with user1
        client = APIClient()
        response = client.post(reverse('articles:create_article'),
                            sample_input, **self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Publish article of user1
        my_url = '/api/articles/{}/publish/'.format(response.data['slug'])
        respo1 = client.patch(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_articles_by_author(self):
        client = APIClient()
        my_url = '/api/profiles/{}/articles/'.format("user1")
        response = client.get(my_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_get_articles_by_non_existent_author(self):
        client = APIClient()
        my_url = '/api/profiles/{}/articles/'.format("user89")
        response = client.get(my_url, **self.header_user1,)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['Articles']['detail'], "The requested profile does not exist.")
    
    def test_get_articles_for_currently_logged_in_user(self):
        client = APIClient()
        my_url = '/api/user/articles/'
        response = client.get(my_url, **self.header_user1,)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_report_an_article(self):
        # Create article with user1
        client = APIClient()
        respo = client.post(reverse('articles:create_article'),
                            self.sample_input, **self.header_user1, format='json')
        self.assertEqual(respo.status_code, status.HTTP_201_CREATED)

        # Publish article of user1
        my_url = '/api/articles/{}/publish/'.format(respo.data['slug'])
        respo1 = client.patch(
            my_url,
            **self.header_user1,
            format='json'
        )
        self.assertEqual(respo1.status_code, status.HTTP_200_OK)
        my_url = '/api/articles/{}/report/'.format(respo.data['slug'])
        response = client.post(reverse('articles:report-article',args=[respo.data['slug']]),
                               self.report_sample, **self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_report_a_non_existent_article(self):
        # Create article with user1
        client = APIClient()
        my_url = '/api/articles/{}/report/'.format("miaomoioaa")
        response = client.post(my_url, self.report_sample, **self.header_user1, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()['report_details']["message"],"you cannot report this article, its does not exist")
    
    def test_get_all_reports(self):
        """ test if superuser can get all article reports """
        client = APIClient()
        response = client.get(reverse(
            'articles:get-all-reports'),**self.header_user2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_all_reports_made_by_a_user(self):
        """ test if a user can get all article reports he made """
        client = APIClient()
        response = client.get(reverse(
            'authentication:user-article-reports'),**self.header_user2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_reports_by_non_superuser(self):
        """ test if a non_superuser can get all article reports """
        client = APIClient()
        response = client.get(reverse(
            'articles:get-all-reports'),**self.header_user1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

