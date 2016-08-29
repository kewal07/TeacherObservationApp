# The client ID (register app in Azure AD to get this value)
id = 'ac92782f-c87a-48e5-9b4d-9ba250c8b11b';
# The client secret (register app in Azure AD to get this value)
secret = 'FJb8apcLnH98+bpg8uPWbqOOur7qF4LZ8oyQDoSZhk4=';

class client_registration:
	@staticmethod
	def client_id():
		return id;
	    
	@staticmethod
	def client_secret():
		return secret;
