import json
import os

# Nome do arquivo para armazenar o estado
STATE_FILE = "auth_state.json"

# Função para definir o estado de login
def set_logged(status, user=None):
    """
    Define o estado de login como True ou False.
    Pode opcionalmente armazenar informações do usuário.
    """
    state = {'logged': status}
    if user and status:
        state['user'] = {
            'id': user.get('id'),
            'nome': user.get('nome'),
            'cargo': user.get('cargo'),
            'username': user.get('username'),
            'senha': user.get('senha')
        }
    save_state(state)
    print(f"Estado de login definido como: {status}")

# Função para verificar se está logado
def is_logged():
    """Retorna True se o usuário estiver logado, senão False."""
    state = load_state()
    return state.get('logged', False)

# Função para limpar login e dados do usuário
def clear_logout():
    """Limpa o estado de login e os dados do usuário."""
    save_state({'logged': False})
    print("Usuário deslogado e informações limpas.")

# Função auxiliar para salvar o estado no arquivo JSON
def save_state(state):
    """Salva o estado no arquivo JSON."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def get_logged_user():
    """
    Retorna os dados do usuário logado, ou None se não houver usuário logado.
    """
    state = load_state()
    if state.get('logged'):
        return state.get('user')
    return None

# Função auxiliar para carregar o estado do arquivo JSON
def load_state():
    """Carrega o estado do arquivo JSON."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {'logged': False}

# Exemplo de uso

