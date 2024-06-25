# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from urllib.parse import urlencode, quote
from random import randint
import requests
import scrapy
from json import dumps
import random

import scrapy.exceptions


class ScrapeOpsFakeUserAgentMiddleware:
    """
    Middleware Scrapy pour utiliser des User-Agents aléatoires de ScrapeOps.

    Ce middleware permet de changer dynamiquement le User-Agent de chaque requête
    pour simuler des utilisateurs différents et éviter la détection des bots.

    Attributs:
        api_key (str): La clé API pour accéder aux services de ScrapeOps.
        scrapeops_endpoint (str): L'URL de l'endpoint pour récupérer les User-Agents.
        scrapeops_fake_user_agents_active (bool): Indique si le changement de User-Agent est activé.
        scrapeops_num_results (int): Le nombre de User-Agents à récupérer.
        headers_list (list): La liste des User-Agents récupérés.

    Méthodes:
        from_crawler(cls, crawler): Initialise le middleware à partir des paramètres du crawler.
        _get_user_agents_list(): Récupère la liste des User-Agents depuis l'API ScrapeOps.
        _get_random_user_agent(): Sélectionne un User-Agent aléatoire de la liste récupérée.
        _scrapeops_fake_user_agents_enabled(): Vérifie si le changement de User-Agent est activé.
        process_request(request, spider): Modifie les requêtes en ajoutant un User-Agent aléatoire.
    """

    @classmethod
    def from_crawler(cls, crawler):
        """
        Initialise le middleware à partir des paramètres du crawler.

        Cette méthode est appelée par Scrapy pour créer une instance du middleware
        en utilisant les paramètres du crawler.

        Args:
            crawler (scrapy.crawler.Crawler): Le crawler Scrapy en cours d'exécution.

        Returns:
            ScrapeOpsFakeUserAgentMiddleware: Une instance du middleware initialisée avec les paramètres du crawler.
        """
        return cls(crawler.settings)
    

    def __init__(self, settings):
        """
        Initialise le middleware ScrapeOpsFakeUserAgentMiddleware avec les paramètres du crawler.
        Args:
            settings (scrapy.settings.Settings): Les paramètres de configuration de Scrapy.
        Attributs:
            api_key (str): La clé API pour accéder aux services de ScrapeOps.
            scrapeops_endpoint (str): L'URL de l'endpoint pour récupérer les User-Agents.
            scrapeops_fake_user_agents_active (bool): Indique si le changement de User-Agent est activé.
            scrapeops_num_results (int): Le nombre de User-Agents à récupérer.
            headers_list (list): La liste des User-Agents récupérés.
        """
        self.api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = settings.get('SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT', 'http://headers.scrapeops.io/v1/user-agents?') 
        self.scrapeops_fake_user_agents_active = settings.get('SCRAPEOPS_FAKE_USER_AGENT_ENABLED', False)
        self.scrapeops_num_results = settings.get('SCRAPEOPS_NUM_RESULTS')
        self.headers_list = []
        self._get_user_agents_list()
        self._scrapeops_fake_user_agents_enabled()

    def _get_user_agents_list(self):
        """
        Récupère la liste des User-Agents depuis l'API ScrapeOps.
        Envoie une requête à l'API ScrapeOps pour obtenir une liste de User-Agents
        que le middleware pourra utiliser pour chaque requête.
        Args:
            Aucun
        Returns:
            None
        """
        payload = {'api_key': self.api_key}
        if self.scrapeops_num_results is not None:
            payload['num_results'] = self.scrapeops_num_results
        response = requests.get(self.scrapeops_endpoint, params=urlencode(payload))
        json_response = response.json()
        self.user_agents_list = json_response.get('result', [])

    def _get_random_user_agent(self):
        """
        Sélectionne un User-Agent aléatoire de la liste récupérée.
        Args:
            Aucun
        Returns:
            str: Un User-Agent aléatoire.
        """
        random_index = randint(0, len(self.user_agents_list) - 1)
        return self.user_agents_list[random_index]

    def _scrapeops_fake_user_agents_enabled(self):
        """
        Vérifie si le changement de User-Agent est activé.
        Si la clé API n'est pas définie ou si l'option de changement de User-Agent est désactivée,
        cette méthode désactive le changement de User-Agent.
        Args:
            Aucun
        Returns:
            None
        """
        if self.api_key is None or self.api_key == '' or self.scrapeops_fake_user_agents_active == False:
            self.scrapeops_fake_user_agents_active = False
        self.scrapeops_fake_user_agents_active = True
    
    def process_request(self, request, spider):
        """
        Modifie les requêtes en ajoutant un User-Agent aléatoire.
        Cette méthode est appelée pour chaque requête et remplace le User-Agent par un
        User-Agent aléatoire de la liste récupérée.
        Args:
            request (scrapy.http.Request): La requête Scrapy actuelle.
            spider (scrapy.Spider): Le spider Scrapy en cours d'exécution.
        Returns:
            None
        """
        random_user_agent = self._get_random_user_agent()
        request.headers['User-Agent'] = random_user_agent
        spider.logger.info(f'User-Agent utilisé: {random_user_agent}')





class ScrapeOpsFakeBrowserHeadersMiddleware:
    """
    Middleware Scrapy pour utiliser des en-têtes de navigateur faux fournis par ScrapeOps.

    Ce middleware permet de remplacer les en-têtes de la requête avec des en-têtes 
    aléatoires récupérés depuis l'API ScrapeOps afin de masquer les requêtes comme 
    celles provenant d'un navigateur réel.

    Attributs:
        api_key (str): La clé API pour accéder au service ScrapeOps.
        scrapeops_endpoint (str): L'URL de l'endpoint pour obtenir les en-têtes de navigateur.
        scrapeops_fake_headers_active (bool): Indique si le remplacement des en-têtes est activé.
        scrapeops_num_results (int): Le nombre d'en-têtes à récupérer.
        headers_list (list): La liste des en-têtes de navigateur récupérés.

    Méthodes:
        from_crawler(cls, crawler): Initialise le middleware à partir des paramètres du crawler.
        __init__(self, settings): Initialise le middleware avec les paramètres de configuration.
        _get_headers_list(self): Récupère la liste des en-têtes de navigateur depuis l'API ScrapeOps.
        _get_random_header(self): Sélectionne un en-tête aléatoire dans la liste des en-têtes.
        _scrapeops_fake_headers_enabled(self): Vérifie si l'utilisation des en-têtes faux est activée.
        process_request(self, request, spider): Modifie les en-têtes de la requête avant de l'envoyer.
    """

    @classmethod
    def from_crawler(cls, crawler):
        """
        Initialise le middleware à partir des paramètres du crawler.
        Cette méthode est appelée par Scrapy pour créer une instance du middleware
        en utilisant les paramètres du crawler.
        Args:
            crawler (scrapy.crawler.Crawler): Le crawler Scrapy en cours d'exécution.
        Returns:
            ScrapeOpsFakeBrowserHeadersMiddleware: Une instance du middleware initialisée avec les paramètres du crawler.
        """
        return cls(crawler.settings)

    def __init__(self, settings):
        """
        Initialise le middleware ScrapeOpsFakeBrowserHeadersMiddleware avec les paramètres du crawler.
        Args:
            settings (scrapy.settings.Settings): Les paramètres de configuration de Scrapy.
        Attributs:
            api_key (str): La clé API pour accéder au service ScrapeOps.
            scrapeops_endpoint (str): L'URL de l'endpoint pour obtenir les en-têtes de navigateur.
            scrapeops_fake_headers_active (bool): Indique si le remplacement des en-têtes est activé.
            scrapeops_num_results (int): Le nombre d'en-têtes à récupérer.
            headers_list (list): La liste des en-têtes de navigateur récupérés.
        """
        self.api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = settings.get('SCRAPEOPS_FAKE_HEADERS_ENDPOINT', 'http://headers.scrapeops.io/v1/browser-headers?') 
        self.scrapeops_fake_headers_active = settings.get('SCRAPEOPS_FAKE_HEADERS_ENABLED', False)
        self.scrapeops_num_results = settings.get('SCRAPEOPS_NUM_RESULTS')
        self.headers_list = []
        self._get_headers_list()
        self._scrapeops_fake_headers_enabled()

    def _get_headers_list(self):
        """
        Récupère la liste des en-têtes de navigateur depuis l'API ScrapeOps.
        Cette méthode envoie une requête à l'API ScrapeOps pour obtenir une liste
        d'en-têtes de navigateur à utiliser pour masquer les requêtes.
        Args:
            Aucun.
        Returns:
            Aucun. Met à jour l'attribut headers_list avec les en-têtes récupérés.
        """
        payload = {'api_key': self.api_key}
        if self.scrapeops_num_results is not None:
            payload['num_results'] = self.scrapeops_num_results
        response = requests.get(self.scrapeops_endpoint, params=urlencode(payload))
        json_response = response.json()
        self.headers_list = json_response.get('result', [])


    def _get_random_header(self):
        """
        Sélectionne un en-tête aléatoire dans la liste des en-têtes récupérés.
        Cette méthode choisit un en-tête de navigateur au hasard parmi la liste des
        en-têtes récupérés pour remplacer les en-têtes de la requête.
        Args:
            Aucun.
        Returns:
            dict: Un dictionnaire contenant les en-têtes de navigateur sélectionnés.
        """
        random_index = randint(0, len(self.headers_list) - 1)
        return self.headers_list[random_index]


    def _scrapeops_fake_headers_enabled(self):
        """
        Vérifie si l'utilisation des en-têtes faux est activée.
        Cette méthode met à jour l'attribut scrapeops_fake_headers_active pour indiquer
        si le remplacement des en-têtes est activé en fonction de la clé API et de la
        configuration.
        Args:
            Aucun.
        Returns:
            Aucun. Met à jour l'attribut scrapeops_fake_headers_active.
        """
        if self.api_key is None or self.api_key == '' or self.scrapeops_fake_headers_active == False:
            self.scrapeops_fake_headers_active = False
        self.scrapeops_fake_headers_active = True
    
    def process_request(self, request, spider):
        """
        Modifie les en-têtes de la requête avant de l'envoyer.
        Cette méthode remplace les en-têtes de la requête Scrapy par des en-têtes
        de navigateur aléatoires récupérés depuis l'API ScrapeOps.
        Args:
            request (scrapy.http.Request): La requête Scrapy actuelle.
            spider (scrapy.Spider): L'instance du spider qui effectue la requête.
        Returns:
            Aucun. Met à jour les en-têtes de la requête.
        """    
        random_header = self._get_random_header()
        for key, val in random_header.items():
            request.headers[key] = val
        spider.logger.info(f'Random Header : {random_header}')




class ScrapeOpsProxyMiddleware:
    """
    Middleware Scrapy pour utiliser le proxy ScrapeOps.

    Ce middleware permet de rediriger les requêtes via le proxy ScrapeOps
    en ajoutant les en-têtes nécessaires et en gérant les URL de réponse.

    Attributs:
        scrapeops_api_key (str): La clé API pour accéder au proxy ScrapeOps.
        scrapeops_endpoint (str): L'URL de l'endpoint du proxy ScrapeOps.
        scrapeops_proxy_active (bool): Indique si le proxy ScrapeOps est activé.

    Méthodes:
        from_crawler(cls, crawler): Initialise le middleware à partir des paramètres du crawler.
        process_request(request, spider): Modifie les requêtes avant de les envoyer au serveur.
        process_response(request, response, spider): Modifie les réponses avant de les transmettre au spider.
    """

    @classmethod
    def from_crawler(cls, crawler):
        """
        Initialise le middleware à partir des paramètres du crawler.
        Cette méthode est appelée par Scrapy pour créer une instance du middleware
        en utilisant les paramètres du crawler.
        Args:
            crawler (scrapy.crawler.Crawler): Le crawler Scrapy en cours d'exécution.
        Returns:
            ScrapeOpsProxyMiddleware: Une instance du middleware initialisée avec les paramètres du crawler.
        """
        return cls(crawler.settings)


    def __init__(self, settings):
        """
        Initialise le middleware ScrapeOpsProxyMiddleware avec les paramètres du crawler.
        Args:
            settings (scrapy.settings.Settings): Les paramètres de configuration de Scrapy.
        Attributs:
            api_key (str): La clé API pour accéder au proxy ScrapeOps.
            scrapeops_endpoint (str): L'URL de l'endpoint du proxy ScrapeOps.
            scrapeops_proxy_active (bool): Indique si le proxy ScrapeOps est activé.
        """
        self.api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = settings.get('SCRAPEOPS_FAKE_PROXY_ENDPOINT', 'https://proxy.scrapeops.io/v1/?') 
        self.scrapeops_proxy_active = settings.get('SCRAPEOPS_PROXY_ENABLED', False)
        self.session_number = 1


    # @staticmethod
    # def _param_is_true(request, key):
    #     """
    #     Vérifie si un paramètre spécifique dans les métadonnées de la requête est défini comme vrai.
    #     Args:
    #         request (scrapy.http.Request): La requête Scrapy actuelle.
    #         key (str): La clé du paramètre à vérifier dans les métadonnées de la requête.
    #     Returns:
    #         bool: True si le paramètre est défini comme vrai, False sinon.
    #     """
    #     if request.meta.get(key) or request.meta.get(key, 'false').lower() == 'true':
    #     # if request.meta.get(key, 'false').lower() == 'true':
    #         return True
    #     return False
    
    @staticmethod
    def _param_is_true(request, key):
        value = request.meta.get(key, False)
        if isinstance(value, str):
            if value.lower() == 'true':
                value = True
        if isinstance(value, bool):
            return value
        else:
            return False
    
    @staticmethod
    def random_value(min_value, max_value):
        """
        Génère une valeur aléatoire entre min_value et max_value.
        Args:
            min_value (int): Valeur minimale.
            max_value (int): Valeur maximale.
        Returns:
            int: Valeur aléatoire.
        """
        return random.randint(min_value, max_value)
    
    @staticmethod
    def _js_scenario():
        """
        Construit et retourne un scénario JavaScript pour l'interaction avec une page web.
        Returns:
            str: Scénario JavaScript encodé.
        """
        js_scenario = {
                "instructions": [
                    {"wait": ScrapeOpsProxyMiddleware.random_value(10000,20000)},
                    {"scroll_y": ScrapeOpsProxyMiddleware.random_value(1000,4000)},
                    {"wait_for": "li> a"},
                    {"wait": ScrapeOpsProxyMiddleware.random_value(100,200)},
                    {"click": "li> a"},
                    {"wait": ScrapeOpsProxyMiddleware.random_value(10,100)},
                    {"scroll_x": ScrapeOpsProxyMiddleware.random_value(1000,4000)},
                    # {"wait": ScrapeOpsProxyMiddleware.random_value(10,100)},
                    # {"fill": ["#input_field", "valeur_à_saisir"]},
                    {"wait": ScrapeOpsProxyMiddleware.random_value(10,100)},
                    {"evaluate": "console.log('Interaction terminée')"}
                ]
            }
        js_scenario_string = dumps(js_scenario)
        return js_scenario_string
    


    def _get_proxy_url(self, request):
        """
        Génère l'URL du proxy ScrapeOps avec les paramètres appropriés.
        Args:
            request (scrapy.http.Request): La requête Scrapy actuelle.
        Returns:
            str: L'URL du proxy ScrapeOps avec les paramètres codés.
        """
        payload = {'api_key': self.api_key, 'url': request.url}
        if self._param_is_true(request, 'sops_render_js'):
            payload['render_js'] = True
        if self._param_is_true(request, 'sops_residential'): 
            payload['residential'] = True
        if self._param_is_true(request, 'sops_keep_headers'): 
            payload['keep_headers'] = True
        if self._param_is_true(request, 'sops_country'):
            payload['country'] = 'us'
        if self._param_is_true(request, 'sops_js_scenario'):
            payload['js_scenario'] = self._js_scenario()
        if self._param_is_true(request, 'sops_session_number'):
            payload['session_number'] = 1
        if self._param_is_true(request, 'sops_follow_redirects'):
            payload['follow_redirects'] = False
        if self._param_is_true(request, 'sops_initial_status_code'):
            payload['initial_status_code'] = True
        if self._param_is_true(request, 'sops_final_status_code'):
            payload['final_status_code'] = True
        if self._param_is_true(request, 'sops_premium'):
            payload['premium'] = True
        if self._param_is_true(request, 'sops_optimize_request'):
            payload['optimize_request'] = True
        if self._param_is_true(request, 'sops_max_request_cost'):
            payload['max_request_cost'] = 50
        if self._param_is_true(request, 'sops_bypass'):
            payload['bypass'] = 'generic_level_1'
        proxy_url = self.scrapeops_endpoint + urlencode(payload)
        return proxy_url
    


    def _scrapeops_proxy_enabled(self):
        """
        Vérifie si le proxy ScrapeOps est activé.
        Returns:
            bool: True si le proxy ScrapeOps est activé et que la clé API est définie, False sinon.
        """
        if self.api_key is None or self.api_key == '' or self.scrapeops_proxy_active == False:
            return False
        return True
    


    def _get_IP_proxy(self, spider):
        try:
            # Construire l'URL encodée pour obtenir l'adresse IP via le proxy
            ip_url = quote('https://api.ipify.org?format=json', safe='')
            proxy_url = f'{self.scrapeops_endpoint}api_key={self.api_key}&url={ip_url}'
            response = requests.get(proxy_url)
            response.raise_for_status()  # Vérifie si la requête a échoué
            ip_address = response.json().get('ip')
            return ip_address
        except requests.exceptions.RequestException as e:
            spider.logger.error(f'Erreur lors de la récupération de l\'IP : {e}')
        except ValueError as e:
            spider.logger.error(f'Erreur lors de la conversion JSON : {e}')
            spider.logger.error(f'Response content: {response.text}')
        return None


    def _add_original_url_to_request_headers(self, request):
        """
        Ajoute l'URL originale aux en-têtes de la requête.
        Args:
            request (scrapy.Request): La requête Scrapy à laquelle ajouter l'en-tête.
        """
        request.headers['X-Original-URL'] = request.url

        

    def _replace_response_url(self,response, request):
        """
        Remplace l'URL de la réponse par l'URL originale stockée dans les en-têtes de la requête.
        Args:
            response (scrapy.http.Response): La réponse Scrapy à modifier.
            request (scrapy.Request): La requête Scrapy contenant l'URL originale dans les en-têtes.
        Returns:
            scrapy.http.Response: La réponse modifiée avec l'URL originale.
        """
        original_url = request.headers.get('X-Original-URL', response.url).decode(response.headers.encoding)
        replace_response = response.replace(url=original_url)
        return replace_response


    # Requête avant envoie au serveur
    """
    Traite les requêtes avant de les envoyer au serveur en utilisant le proxy ScrapeOps.

    Cette méthode modifie les requêtes pour les rediriger via le proxy ScrapeOps, ajoute
    l'URL originale aux en-têtes de la requête, et génère une nouvelle requête avec l'URL
    du proxy. Si le proxy ScrapeOps n'est pas activé ou si l'URL de l'endpoint est déjà
    présente dans la requête, la requête est envoyée telle quelle.

    Args:
        request (scrapy.Request): La requête Scrapy actuelle à traiter.
        spider (scrapy.Spider): Le spider Scrapy en cours d'exécution.

    Returns:
        scrapy.Request: La nouvelle requête modifiée avec l'URL du proxy, ou None si le proxy n'est pas utilisé.
    """
    def process_request(self, request, spider):
        if self._scrapeops_proxy_enabled is False or self.scrapeops_endpoint in request.url:
            return None
        self._add_original_url_to_request_headers(request)
        spider.logger.info(f'URL stockée dans les headers de la requête')
        proxy_url = self._get_proxy_url(request)
        new_request = request.replace(cls=scrapy.Request, url=proxy_url, meta=request.meta)
        spider.logger.info(f'META : {request.meta}')
        spider.logger.info(f'URL proxy envoyée au Serveur : {proxy_url}')
        # proxy_ip = self._get_IP_proxy(spider)
        # if proxy_ip:
        #     spider.logger.info(f'IP utilisée par le proxy : {proxy_ip}')
        return new_request
    
    # Response serveur avant envoie au spider
    def process_response(self, request, response, spider):
        """
        Traite la réponse reçue du serveur avant de la transmettre au spider.
        Cette méthode remplace l'URL de la réponse par l'URL d'origine stockée dans les headers de la requête,
        puis enregistre cette nouvelle URL dans les logs.
        Args:
            request (scrapy.Request): La requête originale envoyée au serveur.
            response (scrapy.http.Response): La réponse reçue du serveur.
            spider (scrapy.Spider): L'instance du spider qui effectue la requête.
        Returns:
            scrapy.http.Response: La réponse modifiée avec l'URL d'origine remplacée.
    """
        new_response = self._replace_response_url(response, request)
        spider.logger.info(f'URL envoyée au Spider : {new_response.url}')
        return new_response
    



    # def process_exception(self, request, exception, spider):
    #     if isinstance(exception, scrapy.exceptions.IgnoreRequest):
    #         spider.logger.error('Requête ignorée')
    #     elif '401' in str(exception):
    #         spider.logger.error('Erreur 401 : Crédits ScrapeOps épuisés. Arrêt du scraper.')
    #         raise scrapy.exceptions.CloseSpider('ScrapeOps credits exhausted')
    #     else:
    #         spider.logger.error(f'Exception non gérée : {exception}')

    