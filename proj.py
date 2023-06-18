import flask
import logging
import psycopg2
import jwt
import time
import random

app = flask.Flask(__name__)
secret_key = '#FF8723#'
token = ''

# criar os id todos da mesma forma
# meter a playlist na detail artist
# play playlist


StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}


def db_connection():
    db = psycopg2.connect(
        user='projeto_bd',
        password='password',
        host='127.0.0.1',
        port='5432',
        database='testdummie'
    )

    return db


@app.route('/')
def landing_page():
    return """
    Bem-vindo!!<br/>
    """

 # set up logging
logging.basicConfig(filename='log_file.log')
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)


# User Registration
@app.route('/spotivinho_DB/user/registration', methods=['POST'])
def registration():
    logger.info('POST /spotivinho_DB/user/registration')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /spotivinho_DB/user/registration - payload: {payload}')

    # verifica se tá tudo ok na payload (validaçao de argumentos)
    if 'username' not in payload or 'email' not in payload or 'password' not in payload or 'nome' not in payload or 'data_nasc' not in payload or 'pais' not in payload or 'genero' not in payload:
        response = {
            'status': StatusCodes['api_error'], 'results': 'Missing required fields'}
        conn.close()
        return flask.jsonify(response)

    num_random = str(random.randint(0, 999999))
    id = f"{payload['username']}{num_random}"

    statement = 'INSERT INTO utilizador (username,email,password,user_id) VALUES (%s, %s, %s, %s)'
    statement2 = 'INSERT INTO consumidor (nome,data_nasc,pais,genero,utilizador_user_id) VALUES (%s,%s,%s,%s,%s)'

    values = (payload['username'], payload['email'],
              payload['password'], id)
    values2 = (payload['nome'], payload['data_nasc'],
               payload['pais'], payload['genero'], id)

    try:
        # verifica se utilizador existe
        cur.execute("SELECT * FROM utilizador WHERE username = %s",
                    (payload['username'],))
        existing_user = cur.fetchone()

        if existing_user:
            response = {
                'status': StatusCodes['api_error'], 'results': 'Utilizador já existe!'}
            conn.close()
            return flask.jsonify(response)
        else:
            # inserir novo utilizador
            cur.execute("BEGIN TRANSACTION")
            cur.execute(statement, values)
            cur.execute(statement2, values2)
            conn.commit()
            response = {
                'status': StatusCodes['success'], 'results': f'Utilizador {id} criado!'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /spotivinho_DB/user/login - error: {error}')
        response = {
            'status': StatusCodes['internal_error'], 'errors': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# registar novo artista
@app.route('/spotivinho_DB/user/artista', methods=['POST'])
def novo_artista():
    logger.info('POST /spotivinho_DB/user/artista')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    # logger.debug(f'POST /spotivinho_DB/user/artista - payload: {payload}')
# verifica se está tudo na payload
    if "username" not in payload or "password" not in payload or "email" not in payload or "nome" not in payload or "idade" not in payload or "genero" not in payload or "nib" not in payload or "pais" not in payload or "data_nasc" not in payload or "label_id" not in payload or "token" not in payload:
        response = {
            'status': StatusCodes['api_error'], 'results': 'Missing required fields.'}
        conn.close()
        return flask.jsonify(response)

    # verifica se é admin
    
    token = payload['token']
    print(token)
    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)
    if decode['permissao'] == "administrador":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        conn.close()
        return flask.jsonify(response)

    # cria user id
    num_random = str(random.randint(0, 999999))
    user_id = f"{payload['username']}{num_random}"

    # querys a ser feitas
    statement = 'INSERT INTO utilizador (username,email,password,user_id) VALUES (%s, %s, %s, %s)'
    statement2 = 'INSERT INTO artista (nome,idade,nib,genero,pais,data_nasc,label_label_id,utilizador_user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'

    values = (payload['username'], payload['email'],
              payload['password'], user_id)
    values2 = (payload['nome'], payload['idade'], payload['nib'], payload['genero'],
               payload['pais'], payload['data_nasc'], payload['label_id'], user_id)

    try:

        cur.execute("SELECT * FROM utilizador WHERE username = %s",
                    (payload['username'],))
        existing_user = cur.fetchone()

        if existing_user:
            response = {
                'status': StatusCodes['api_error'], 'results': 'Username já existe!'}
            conn.close()
            return flask.jsonify(response)

        else:
            # inserir novo artista
            cur.execute("BEGIN TRANSACTION")
            cur.execute(statement, values)
            cur.execute(statement2, values2)
            conn.commit()
            response = {
                'status': StatusCodes['success'], 'results': f'artista {user_id} criado!'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /spotivinho_DB/user/artista - error: {error}')
        response = {
            'status': StatusCodes['internal_error'], 'errors': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

# User authentication
@app.route('/spotivinho_DB/user/auth', methods=['PUT'])
def user_auth():
    logger.info('/spotivinho_DB/user/auth')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'PUT /spotivinho_DB/user/auth - payload: {payload}')

    if 'username' not in payload or 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Insira password e username.'}
        conn.close()
        return flask.jsonify(response)
    logger.debug(payload['username'])

    try:
        cur.execute("SELECT user_id FROM utilizador WHERE username = %s AND password = %s",
                    (payload['username'], payload['password']))
        existing_user = cur.fetchone()
        logger.debug(existing_user)
        if existing_user:
            # verifica o tipo de utilizador, retorna uma string ("admin"/ "artista" / "consumidor")
            permissao = role(existing_user)

            # encodifica no token a permissao e user id de quem faz login
            payload["permissao"] = permissao
            payload["user_id"] = existing_user[0]

            # duraçao do token definida em segundos (1 hora)
            duracao_token = 3600
            # tempo atual
            tempo_atual = int(time.time())
            tempo_exp = tempo_atual + duracao_token

            payload["duracao_token"] = tempo_exp

            logger.debug(f'payload - {payload}')

            token = jwt.encode(payload, secret_key, algorithm='HS256')
            response = {
                'status': StatusCodes['success'], 'results': f"{token} "}

        else:
            response = {
                'status': StatusCodes['api_error'], 'results': 'Credenciais incorretas.'}
            conn.close()
            return flask.jsonify(response)

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response = {
            'status': StatusCodes['internal_error'], 'errors': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)

# Add song
@app.route('/spotivinho_DB/song', methods=['POST'])
def add_song():
    logger.info('POST /spotivinho_DB/song')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /spotivinho_DB/song - payload: {payload}')

    # falta um if para verificar se existe o campo outros artistas, de modo
    if "duracao" not in payload or "pub_data" not in payload or "genero" not in payload or "label_id" not in payload or "titulo" not in payload or "audio" not in payload or "album_album_id" not in payload or 'token' not in payload:
        response = {
            'status': StatusCodes['api_error'], 'results': 'Missing required fields'}
        return flask.jsonify(response)

    token = payload['token']

    # verifica se é artista
    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)
    if decode['permissao'] == "artista":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        return flask.jsonify(response)

    statement = """INSERT into musica (ismn,duracao,pub_data,genero,label_id,titulo,audio,album_id,artista_utilizador_user_id) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    statement1 = "INSERT INTO outros_artistas(musica_ismn,artista_utilizador_user_id,artista_nome,musica_nome) VALUES (%s,%s,%s,%s)"
    statement2 = "SELECT nome from artista WHERE utilizador_user_id = %s"
    num_random = str(random.randint(0, 999999))
    id = f"{payload['titulo']}{num_random}"
    try:
        artista_id = str(decode['user_id'])
        values = (str(id), payload["duracao"], payload["pub_data"], payload["genero"],
                  payload["label_id"], payload["titulo"], payload["audio"], payload["album_album_id"], artista_id)
        cur.execute("BEGIN TRANSACTION")
        cur.execute(statement, values)
        if "outros_artistas" in payload:
            outros_artistas = str(payload['outros_artistas']).split(",")
    
            if type(outros_artistas) == str:
                cur.execute(statement2,(outros_artistas[0]))
                nome = cur.fetchone()
                values = (str(id),outros_artistas,nome,payload['titulo']) 
                cur.execute(statement1,values)
            else:
                for i in range(len(outros_artistas)):
                    cur.execute(statement2,(outros_artistas[i],))
                    nome = cur.fetchone()
                    values = (str(id),outros_artistas[i],nome,payload['titulo'])
                    cur.execute(statement1,values)
        conn.commit()
        response = {
            'status': StatusCodes['success'], 'results': f'nova musica, com o ismn - {str(id)} adicionada com sucesso!'}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /spotivinho_DB/song - error: {error}')
        response = {
            'status': StatusCodes['internal_error'], 'errors': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# Add album
# falta meter a tracklist correta
@app.route('/spotivinho_DB/album', methods=['POST'])
def add_album():
    logger.info('POST /spotivinho_DB/album')

    # tou a pensar isto deveria ser sempre a primeira coisa, não deve fazer nada antes de verificar se tem autorização, certo?
    # verifica se é artista
    payload = flask.request.get_json()
    if 'tracklist' not in payload or 'titulo' not in payload or 'duracao' not in payload or 'pub_data' not in payload or 'token' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Missing required fields'}
        return flask.jsonify(response)
    token = payload['token']
    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)
    if decode['permissao'] == "artista":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        return flask.jsonify(response)

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /spotivinho_DB/album - payload: {payload}')
    num_random = str(random.randint(0, 999999))
    id = f"{payload['titulo']}{num_random}"
    statement = "Select ismn from musica where ismn = %s"
    statement4 = "Select album_id from album where album_id = %s"
    statement2 = "INSERT into musica (ismn,duracao,pub_data,genero,label_id,titulo,audio,album_id,artista_utilizador_user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    statement3 = "INSERT into album (album_id,album_name,duracao,artista_utilizador_user_id,pub_data) VALUES (%s,%s,%s,%s,%s)"
    statement5 = "INSERT INTO album_track (album_album_id,musica_ismn) VALUES (%s,%s)"
    statement6 = "INSERT INTO outros_artistas (artista_utilizador_user_id,musica_ismn,artista_nome,musica_nome) VALUES (%s,%s,%s,%s)"
    statement7 = "SELECT nome FROM artista WHERE utilizador_user_id = %s"
    values = (id, payload['titulo'],
              payload['duracao'], decode['user_id'], payload['pub_data'])

    tracklist = payload['tracklist'].split("/")
    novidades = "músicas adicionadas:\n"

    try:
        # verifica se album existe
        cur.execute(statement4, (payload['album_id'],))
        if cur.fetchone():
            response = {'status': StatusCodes['api_error'],
                        'results': f'Album {payload["titulo"]} já existe.'}
            return flask.jsonify(response)

        cur.execute("BEGIN TRANSACTION")
        # insere album, necessário inserir album primeiro para poder inserir músicas
        cur.execute(statement3, values)

        # verifica as músicas da tracklist uma a uma se já existem na base de dados, adiciona as que não existem
        for row in tracklist:
            musica = row.split(",")
            # se música não tem os campos necessários, adicionar caso para verificar campo "outros_artistas", na função add_song também falta.
            if len(musica) < 7:
                response = {
                    'status': StatusCodes['api_error'], 'results': f'missing required fields in musica'}
                return flask.jsonify(response)
            if len(musica) == 7:
                # isto só é necessário para selects, nos inserts nao da
                cur.execute(statement, (musica[0],))
                # verifica se a música existe
                if cur.fetchone():
                    pass
                else:
                    values = (musica[0], musica[1], musica[2], musica[3], musica[4],
                            musica[5], musica[6], id, decode['user_id'])
                    # adiciona à base de dados
                    cur.execute(statement2, values)
                    novidades = novidades + "- " + musica[5] + "\n"
            else:
                # isto só é necessário para selects, nos inserts nao da
                cur.execute(statement, (musica[0],))
                # verifica se a música existe
                if cur.fetchone():
                    pass
                else:
                    values = (musica[0], musica[1], musica[2], musica[3], musica[4],
                            musica[5], musica[6], id, decode['user_id'])
                    # adiciona à base de dados
                    cur.execute(statement2, values)
                    novidades = novidades + "- " + musica[5] + "\n"
                    for i in range(len(musica)-7):
                        cur.execute(statement7,(musica[i+7],))
                        nome = cur.fetchone()
                        values = (musica[i+7],musica[0],nome,musica[5])
                        cur.execute(statement6,values)
            
        for row in tracklist:
            musica = row.split(",")
            values = (id,musica[0])
            cur.execute(statement5,values)

        response = {
            'status': StatusCodes['success'], 'results': f"album {payload['titulo']}adicionado com sucesso, músicas adicionadas:\n {novidades}"
        }
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /spotivinho_DB/song - error: {error}')
        response = {
            'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# Search song não verifica login
#NAO CONSEGUIMOS FAZER SO UMA QUERY SEM TER NA TABELA OUTROS ARTISTAS O NOME DO ARTISTA TAMBEM
@app.route('/spotivinho_DB/song/<titulo>', methods=['GET'])
def search_song(titulo):
    logger.info('GET /spotivinho_DB/song/<titulo>')

    logger.debug(f'titulo: {titulo}')
    conn = db_connection()
    cur = conn.cursor()
    var = '%'
    statement = """SELECT musica.titulo, artista.nome,album.album_name,outros_artistas.musica_nome,musica.genero,musica.duracao
FROM musica
INNER JOIN artista ON musica.artista_utilizador_user_id = artista.utilizador_user_id 
INNER JOIN album ON musica.album_id = album.album_id 
LEFT JOIN outros_artistas ON musica.ismn = outros_artistas.musica_ismn
WHERE musica.titulo LIKE %s || %s || %s
  """
    payload = flask.request.get_json()
    if 'token' not in payload:
        response = {'status':StatusCodes['api_error'],
                    'results':"Missing required fields"}

    token = payload['token']
    # verificar login efectuado

    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)
    if decode['permissao'] == "consumidor":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        conn.close()
        return flask.jsonify(response)


    try:
        cur.execute(statement, (var, titulo, var))
        rows = cur.fetchall()
        Results = []
        #logger.debug(rows)
        print(rows)
        for row in rows:
            if row[3] is not None:
                content = {'titulo':                row[0],
                        'artistas':                 row[1],
                        'album':                    row[2],
                        'artistas_associados':      row[3],
                        'genero':                   row[4],
                        'duracao':                  row[5]
                        }
                Results.append(content)
            else:
                content = {'titulo':                row[0],
                        'artistas':                 row[1],
                        'album':                    row[2],
                        'outros_artistas':          'solo',
                        'genero':                   row[4],
                        'duracao':                  row[5]
                        }
                Results.append(content)
        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /spotivinho_DB/song - error: {error}')
        response = {
            'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# ---------TIAGO
# Detail Artist
# neste momento só mostra todas as musicas e albuns da sua autoria falta meter playlist
# este nem quis testar, sei que falta aqui muita cena, mas so me parece que vale a pena resolver
# verificar login
@app.route('/spotivinho_DB/artista_info/<artist_id>', methods=['GET'])
def detail_artist(artist_id):
    logger.info('GET /spotivinho_DB/artista_info/<artist_id>')

    logger.debug(f'artist_id: {artist_id}')

    conn = db_connection()
    cur = conn.cursor()

    payload = flask.request.get_json()
    if 'token' not in payload:
        response = {'status':StatusCodes['api_error'],
                    'results':"Missing required fields"}

    token = payload['token']
    # verificar login efectuado

    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)
    if decode['permissao'] == "consumidor":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        conn.close()
        return flask.jsonify(response)


    statement = """SELECT artista.nome,artista.label_label_id, musica.titulo, album.album_name, outros_artistas.musica_nome,playlist.titulo
FROM artista
LEFT JOIN musica ON artista.utilizador_user_id = musica.artista_utilizador_user_id
LEFT JOIN album ON artista.utilizador_user_id = album.artista_utilizador_user_id
LEFT JOIN outros_artistas ON artista.utilizador_user_id = outros_artistas.artista_utilizador_user_id
LEFT JOIN playlist_track ON musica.ismn = playlist_track.musica_ismn
LEFT JOIN playlist ON playlist_track.playlist_playlist_id = playlist.playlist_id and playlist.visibility = 'public'
WHERE artista.utilizador_user_id = %s"""

    try:

        cur.execute(statement, (artist_id,))
        rows = cur.fetchall()

        logger.debug(rows)
        Results = []
        Label = []
        musicas = []
        Albuns = []
        features = []
        playlist = []
        content = {
            'Artista': rows[0][0]}
        Results.append(content)
        for row in rows:
            if row[1] not in Label and row[1]:
               Label.append(row[1])
            if row[2] not in musicas and row[2]:               
                musicas.append(row[2])
            if row[3] not in Albuns and row[3]:
                Albuns.append(row[3]) 
            if row[4] not in features and row[4]:
                features.append(row[4])
            if row[5] not in playlist and row[5]:
                playlist.append(row[5])
        Values = {
            'Labels':Label,
            'musicas': musicas,
            'Albuns': Albuns,
            'features': features,
            'playlist': playlist
        }
        Results.append(Values)
    
        response = {'status': StatusCodes['success'], 'results': Results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(
            f'GET /spotivinho_DB/artista_info/<artista_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'],
                    'errors': str(error)}

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# sub premium
# perguntar prof se os cartoes pre pagos introduzidos pelo user ficam todoss como usados
# ou apenas os que sao necessarios usar ficam para o user e os restantes como novo
@app.route('/spotivinho_DB/subscription', methods=['POST'])
def subscribe():
    logger.info('POST /spotivinho_DB/subscription')

    conn = db_connection()
    cur = conn.cursor()

    payload = flask.request.get_json()

    logger.debug(f'POST /spotivinho_DB/subscription - payload: {payload}')

    if "period" not in payload or "cards" not in payload or "token" not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Missing required fields.'}
        return flask.jsonify(response)

    token = payload['token']
    # verificar login efectuado

    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)
    if decode['permissao'] == "consumidor":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        conn.close()
        return flask.jsonify(response)

    # PLANOS DE SUBSCRIÇAO -->(month 7€, quarter 21€, semester 42€)

    statement = "SELECT customer_id,valor FROM pre_paid WHERE pre_paid_id = %s"

    try:
        if payload['period'] not in ('month', 'quarter', 'semester'):
            response = {'status': StatusCodes['api_error'],
                        'results': 'Período deve ser month, quarter, semester.'}
            conn.close()
            return flask.jsonify(response)

        cartoes = str(payload['cards']).split(',')
        saldo_total = 0

        logger.debug(f'id de cartoes a ser utilizados - {cartoes}')

        # verfica se cartao tem saldo suficiente
        if payload['period'] == "month":
            valor_necessario = 7
        elif payload['period'] == "quarter":
            valor_necessario = 21
        elif payload['period'] == "semester":
            valor_necessario = 42

        for item in cartoes:
            # logger.debug(item)

            cur.execute(statement, (item,))
            verify_card = cur.fetchall()
            logger.debug(f'verify_card - {verify_card}')
            saldo_total += int(verify_card[0][1])

            logger.debug(f'saldo total de todos os cartoes - {saldo_total}')

            # verificar estado do cartao (novo ou utilizado)
            # logger.debug(verify_card[0][0])
            if verify_card[0][0] == 'novo' or verify_card[0][0] == decode['user_id']:
                pass
            else:
                response = {'status': StatusCodes['api_error'],
                            'results': 'Cartão inválido.'}
                conn.close()
                return flask.jsonify(response)

        if saldo_total < valor_necessario:
            response = {'status': StatusCodes['api_error'],
                        'results': 'Saldo insuficiente.'}
            conn.close()
            return flask.jsonify(response)


        statement4 = "SELECT status FROM consumidor WHERE utilizador_user_id = %s"
        values4 = decode['user_id']

        cur.execute(statement4,(values4,))
        data_ultima_sub = cur.fetchone()
        estado = data_ultima_sub

        if estado[0] != "regular":

            data_ultima_sub_struct = time.strptime(data_ultima_sub[0], "%Y-%m-%d")

            timestamp1 = time.mktime(data_ultima_sub_struct)
            timestamp2 = time.mktime(time.localtime())


        if estado[0] == "regular" or timestamp2 > timestamp1:
            if payload['period'] == "month":
                data_atual = time.localtime()
                ano_futuro = data_atual.tm_year + (data_atual.tm_mon + 1) // 12
                mes_futuro = (data_atual.tm_mon + 1) % 12
                if mes_futuro == 0:
                    mes_futuro = 12
                    ano_futuro -= 1
                
                # data_futura = data do fim da subscriçao
                data_futura = "{:04d}-{:02d}-{:02d}".format(ano_futuro, mes_futuro, data_atual.tm_mday)
            
            elif payload['period'] == "quarter":
                data_atual = time.localtime()
                ano_futuro = data_atual.tm_year + (data_atual.tm_mon + 3) // 12
                mes_futuro = (data_atual.tm_mon + 3) % 12
                if mes_futuro == 0:
                    mes_futuro = 12
                    ano_futuro -= 1
                
                # data_futura = data do fim da subscriçao
                data_futura = "{:04d}-{:02d}-{:02d}".format(ano_futuro, mes_futuro, data_atual.tm_mday)

            elif payload['period'] == "semester":
                data_atual = time.localtime()
                ano_futuro = data_ultima_sub_struct.tm_year + (data_atual.tm_mon + 6) // 12
                mes_futuro = (data_atual.tm_mon + 6) % 12
                if mes_futuro == 0:
                    mes_futuro = 12
                    ano_futuro -= 1
                
                # data_futura = data do fim da subscriçao
                data_futura = "{:04d}-{:02d}-{:02d}".format(ano_futuro, mes_futuro, data_atual.tm_mday)
        elif estado[0] != "regular":
            if payload['period'] == "month":

                #cur.execute(statement4,(values4,))
                #data_ultima_sub = cur.fetchone()

                logger.debug(f'data da ultima sub existente - {data_ultima_sub[0]}')
                #data_ultima_sub_formatada = time.strftime("%Y-%m-%d", data_ultima_sub)
                print(10)
                #data_ultima_sub_struct = time.strptime(data_ultima_sub[0], "%Y-%m-%d")

                logger.debug(f'data da ultima sub restruturada - {data_ultima_sub_struct}')

                mes_futuro = (data_ultima_sub_struct.tm_mon + 1) % 12
                ano_futuro = data_ultima_sub_struct.tm_year + (data_ultima_sub_struct.tm_mon + 1) // 12
                
                if mes_futuro == 0:
                    mes_futuro = 12
                    ano_futuro -= 1
                
                # data_futura = data do fim da subscriçao
                data_futura = "{:04d}-{:02d}-{:02d}".format(ano_futuro, mes_futuro, data_ultima_sub_struct.tm_mday)

            elif payload['period'] == "quarter":
                #cur.execute(statement4,(values4,))
                #data_ultima_sub = cur.fetchone()

                logger.debug(f'data da ultima sub existente - {data_ultima_sub[0]}')
                #data_ultima_sub_formatada = time.strftime("%Y-%m-%d", data_ultima_sub)
                #data_ultima_sub_struct = time.strptime(data_ultima_sub[0], "%Y-%m-%d")

                logger.debug(f'data da ultima sub restruturada - {data_ultima_sub_struct}')

                mes_futuro = (data_ultima_sub_struct.tm_mon + 3) % 12
                ano_futuro = data_ultima_sub_struct.tm_year + (data_ultima_sub_struct.tm_mon + 3) // 12
                
                if mes_futuro == 0:
                    mes_futuro = 12
                    ano_futuro -= 1
                
                print(20)
                # data_futura = data do fim da subscriçao
                data_futura = "{:04d}-{:02d}-{:02d}".format(ano_futuro, mes_futuro, data_ultima_sub_struct.tm_mday)

            elif payload['period'] == "semester":
                #cur.execute(statement4,(values4,))
                #data_ultima_sub = cur.fetchone()

                logger.debug(f'data da ultima sub existente - {data_ultima_sub[0]}')
                #data_ultima_sub_formatada = time.strftime("%Y-%m-%d", data_ultima_sub)
                #data_ultima_sub_struct = time.strptime(data_ultima_sub[0], "%Y-%m-%d")

                logger.debug(f'data da ultima sub restruturada - {data_ultima_sub_struct}')
                
                
                mes_futuro = (data_ultima_sub_struct.tm_mon + 6) % 12
                ano_futuro = data_ultima_sub_struct.tm_year + (data_ultima_sub_struct.tm_mon + 6) // 12
                
                if mes_futuro == 0:
                    mes_futuro = 12
                    ano_futuro -= 1
                
                print(20)
                # data_futura = data do fim da subscriçao
                data_futura = "{:04d}-{:02d}-{:02d}".format(ano_futuro, mes_futuro, data_ultima_sub_struct.tm_mday)

        statement2 = "UPDATE consumidor SET status = %s WHERE utilizador_user_id = %s"
        values = (data_futura, decode['user_id'])

        logger.debug(f'values - {values}')

        cur.execute("BEGIN TRANSACTION")
        cur.execute(statement2, values)
        num_random = str(random.randint(0, 999999))
        id = f"{payload['period']}{num_random}"

        # logger.debug(valor_necessario)
        statement5 = "INSERT INTO sub_data(pre_paid_pre_paid_id,historico_sub_sub_id) VALUES (%s,%s)"
         
        ids_cartoes = []
        for i in cartoes:
            cur.execute(statement, (i,))
            logger.debug(f'id do cartao - {i}')
            valor_card = cur.fetchall()
            logger.debug(valor_card)
            if valor_card[0][1] > valor_necessario:
                saldo_final = valor_card[0][1] - valor_necessario
                cur.execute("UPDATE pre_paid SET valor = %s, customer_id = %s WHERE pre_paid_id = %s", (saldo_final,decode['user_id'], i))
                ids_cartoes.append(i)
                break
            elif valor_card[0][1] == valor_necessario:

                saldo_final = saldo_total - valor_necessario
                cur.execute("DELETE FROM pre_paid WHERE pre_paid_id = %s", (i,))
                ids_cartoes.append(i)
                break
            else:
                valor_necessario = valor_necessario - valor_card[0][1]
                #valor_card[0][1] = 0
                logger.debug(f'valor na variavel i - {i}')
                cur.execute("DELETE FROM pre_paid WHERE pre_paid_id = %s", (i,))
                ids_cartoes.append(i)
        
        data_atual_formatada = time.strftime("%Y-%m-%d", time.localtime())

        statement3 = """INSERT INTO historico_sub (data_compra, saldo_na_data, saldo_pos_compra, consumidor_utilizador_user_id, sub_period, sub_id)
                        VALUES (%s, %s, %s, %s, %s, %s)"""
        values3 = (data_atual_formatada, saldo_total, saldo_final,
                decode['user_id'], payload['period'], id)
        cur.execute(statement3, values3)
        for k in ids_cartoes:
            values = (k,id)
            cur.execute(statement5,values)
        conn.commit()

        response = {'status': StatusCodes['success'],
                    'results': f'Subscription id: {id}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /spotivinho_DB/subscription - error: {error}')
        response = {'status': StatusCodes['internal_error'],
                    'errors': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# Create playlist 
@app.route('/spotivinho_DB/playlist', methods=['POST'])
def add_playlist():
    logger.info('POST /spotivinho_DB/playlist')
    payload = flask.request.get_json()
    logger.debug(f'POST /spotivinho_DB/playlist - payload: {payload}')

    if 'titulo' not in payload or 'tracklist' not in payload or 'duracao' not in payload or 'descricao' not in payload or 'visibility' not in payload or 'token' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Missing required fields'}
        conn.close()
        return flask.jsonify(response)

    token = payload['token']
    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)


    if decode['permissao'] == "consumidor":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        return flask.jsonify(response)

    statement = "SELECT status FROM consumidor WHERE utilizador_user_id = %s"
    statement1 = "SELECT ismn FROM musica WHERE ismn = %s"
    statement2 = """INSERT INTO playlist (playlist_id,titulo,duracao,descricao,consumidor_utilizador_user_id,visibility ) 
    VALUES (%s,%s,%s,%s,%s,%s)"""
    statement3 = "INSERT INTO playlist_track (playlist_playlist_id,musica_ismn) VALUES (%s,%s)"
    values = decode['user_id']



    conn = db_connection()
    cur = conn.cursor()

    tracklist = payload['tracklist'].split(",")

    try:
        cur.execute(statement, (values,))
        status = cur.fetchone()
        status = status[0]

        # check status
        if status == 'regular':
            response = {'status': StatusCodes['api_error'],
                        'results': 'utilizador tem que ser premium para criar playlists!'}
            conn.close()
            return flask.jsonify(response)
        else:
            status = time.strptime(status, "%Y-%m-%d")
            timestamp1 = time.mktime(status)
            timestamp2 = time.mktime(time.localtime())
            if timestamp1 < timestamp2:
                response = {'status': StatusCodes['api_error'],
                        'results': 'utilizador tem que ser premium para criar playlists!'}
                conn.close()
                return flask.jsonify(response)
                
        # check visibility
        if payload['visibility'] != 'private' and payload['visibility'] != 'public':
            response = {'status': StatusCodes['api_error'],
                        'results': 'visibility só pode ser public ou private'}
            conn.close()
            return flask.jsonify(response)

        playlist_id = "@" + payload['titulo']
        values = (playlist_id, payload['titulo'], payload['duracao'],
                  payload['descricao'], decode['user_id'], payload['visibility'])

        cur.execute("BEGIN TRANSACTION")
        # insere a playlist em playlist
        cur.execute(statement2, values)
        # check se todos os id estão na tabela música
        for item in tracklist:
            values = item
            cur.execute(statement1, (values,))
            if cur.fetchone():
                values = (playlist_id, item)
                cur.execute(statement3, values)
            else:
                conn.rollback()
                response = {'status': StatusCodes['api_error'],
                            'results': f'a música com o id - {item} não está presente na base de dados.'}
                conn.close()
                return flask.jsonify(response)

        response = {'status': StatusCodes['success'],
                    'results': 'nova playlist!!!!!'}
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /spotivinho_DB/playlist - error: {error}')
        response = {
            'status': StatusCodes['internal_error'], 'errors': str(error)}
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# Play song
@app.route('/spotivinho_DB/<song_id>', methods=['PUT'])
def play_song(song_id):
    logger.info('PUT /spotivinho_DB/<song_id>')
    payload = flask.request.get_json()
    logger.debug(f'PUT /spotivinho_DB/<song_id> - payload: {payload}')
    if 'token' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'token não está na payload'}
        conn.close()
        return flask.jsonify(response)
    conn = db_connection()
    cur = conn.cursor()

    token = payload['token']
    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)
    user_id = decode['user_id']
    if decode['permissao'] == 'consumidor':
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'sessão iniciada como consumidor para tocar musica por favor!.'}
        conn.close()
        return flask.jsonify(response)
    statement = "UPDATE musica SET streams = streams + 1 WHERE ismn = %s"
    statement1 = """CREATE OR REPLACE FUNCTION atualizar_top_10_playlist() RETURNS TRIGGER AS $$
DECLARE
  musica RECORD;
BEGIN
  -- Cria a playlist do 0 sempre que há uma música nova
  DELETE FROM top10_playlist WHERE consumidor_utilizador_user_id = %s;

  -- Obtem as 10 musicas mais tocadas no ultimo mês
  FOR musica IN (
    SELECT musica_ismn, COUNT(*) AS total_stream
    FROM historico_stream
    WHERE consumidor_utilizador_user_id = %s
      AND data >= %s
      AND data <= %s
    GROUP BY musica_ismn
    ORDER BY total_stream DESC
    LIMIT 10
  ) LOOP
    -- itera para cada musica retornada, adicionando-a à playlist_top10
    INSERT INTO top10_playlist (consumidor_utilizador_user_id, musica_ismn, streams_last_month)
    VALUES (%s, musica.musica_ismn, musica.total_stream);
  END LOOP;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;"""

    data_atual = time.localtime()
    ano = data_atual.tm_year
    mes = (data_atual.tm_mon - 1) % 12
    if mes == 0:
        mes = 12
        ano -= 1

    data = "{:04d}-{:02d}-{:02d}".format(
        data_atual.tm_year, data_atual.tm_mon, data_atual.tm_mday)

    um_mes_atras = "{:04d}-{:02d}-{:02d}".format(
        ano, mes, data_atual.tm_mday)

    values = (user_id,user_id,um_mes_atras, data,user_id)
    hist_stream(data, song_id, user_id)

    try:
        cur.execute(statement1, values)
        cur.execute(statement, (song_id,))
        conn.commit()
        response = {'status': StatusCodes['success'],
                    'results': "oi"}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /spotivinho_DB/card - error: {error}')
        response = {
            'status': StatusCodes['internal_error'], 'errors': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# ---------MOREIRA
# Generate pre-paid cards
@app.route('/spotivinho_DB/card', methods=['POST'])
def add_card():

    logger.info('POST /spotivinho_DB/card')

    conn = db_connection()
    cur = conn.cursor()

    payload = flask.request.get_json()

    logger.debug(f'POST /spotivinho_DB/card - payload: {payload}')

    # verifica se todos os campos necessários estão na payload
    if "valor" not in payload or "expiration_date" not in payload or "quantidade" not in payload or 'token' not in payload:
        response = {
            'status': StatusCodes['api_error'], 'results': 'Missing required fields.'}
        conn.close()
        return flask.jsonify(response)
    # verifica se é admin

    token = payload['token']
    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)

    if decode['permissao'] == "administrador":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        conn.close()
        return flask.jsonify(response)

    if int(payload['valor'])not in (10, 25, 50):
        response = {'status': StatusCodes['api_error'],
                    'results': 'valor dos pre_paid_cards tem que ser 10, 25 ou 50.'}
        conn.close()
        return flask.jsonify(response)

    statement = "INSERT into pre_paid (pre_paid_id,valor,administrador_utilizador_user_id,expiration_date) VALUES(%s,%s,%s,%s)"
    try:
        # para cada pre_paid criado
        ids = []
        cur.execute("BEGIN TRANSACTION")
        for k in range(int(payload['quantidade'])):
            pre_paid_id = ''
            for i in range(16):
                pre_paid_id += str(random.randint(0, 9))
            admin_id = str(decode['user_id']).strip("'(, )")

            values = (pre_paid_id, int(
                (payload['valor'])), admin_id, payload['expiration_date'])
            ids.append(pre_paid_id)

            cur.execute(statement, values)
        conn.commit()
        if int(payload['quantidade']) > 1:
            response = {
                'status': StatusCodes['success'], 'results': f"{payload['quantidade']} pre-paid cards adicionados! ids - {ids}"}
        else:
            response = {
                'status': StatusCodes['success'], 'results': f"{payload['quantidade']} pre-paid card adicionado! id - {ids[0]}"}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /spotivinho_DB/card - error: {error}')
        response = {
            'status': StatusCodes['internal_error'], 'errors': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


#leave commnet/feedback
# comentario pai
@app.route('/spotivinho_DB/comments/<song_id>', methods =['POST'])
def comment(song_id):
    logger.info('POST /spotivinho_DB/comment/<song_id>')
    payload = flask.request.get_json()

    logger.debug(f'song_id: {song_id}')

    conn = db_connection()
    cur = conn.cursor()

    # verificaçao user 
    token = payload['token']

    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)

    if decode['permissao'] == "consumidor":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        conn.close()
        return flask.jsonify(response)

    if "comment" not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Missing required fields.'}
        conn.close()
        return flask.jsonify(response)
    
    try:
        
        cur.execute("BEGIN TRANSACTION")

        num_random = str(random.randint(0, 999999))
        id = f"comment{num_random}"

        statement = """INSERT INTO comentario_pai (comment,comment_id,musica_ismn,consumidor_utilizador_user_id)
                        VALUES (%s,%s,%s,%s)"""
        values = (payload['comment'],id,song_id,decode['user_id'])
        print("rebentou")

        cur.execute(statement,values)

        response = {'status': StatusCodes['success'],
                    'results': f'comment_id: {id}'}
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /spotivinho_DB/comments/<song_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'],
                    'errors': str(error)}
        conn.rollback()
        return flask.jsonify(response)
    
    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# comentario(resposta ao comentario pai)
@app.route('/spotivinho_DB/comments/<song_id>/<parent_comment_id>', methods = ['POST'])
def comment_response(song_id,parent_comment_id):
    logger.info('POST /spotivinho_Db/comments/<song_id>/<parent_comment_id>')

    logger.debug(f'song_id: {song_id}\nparent_comment_id: {parent_comment_id}')

    conn = db_connection()
    cur = conn.cursor()
    payload = flask.request.get_json()
    token = payload['token']

    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)

    if decode['permissao'] == "consumidor":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        conn.close()
        return flask.jsonify(response)
    
    if "comment" not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Missing required fields.'}
    
    try:
        cur.execute("BEGIN TRANSACTION")

        num_random = str(random.randint(0, 999999))
        id = f"comment{num_random}"

        statement = """INSERT INTO comentario (comment,comment_id,musica_ismn,consumidor_utilizador_user_id,comment_pai_id)
                        VALUES (%s,%s,%s,%s,%s)"""
        values = (payload['comment'],id,song_id,decode['user_id'],parent_comment_id)

        cur.execute(statement,values)

        conn.commit()

        response = {'status': StatusCodes['success'],
                    'results': f'comment_id: {id}'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /spotivinho_DB/comments/<song_id>/<parent_comment_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'],
                    'errors': str(error)}
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return flask.jsonify(response)
#Generate monhtly report
@app.route('/spotivinho_DB/report/<data>',methods = ['GET'])
def monthly_report(data):
    logger.info('GET /spotivinho_DB/report')

    conn = db_connection()
    cur = conn.cursor()

    data_atual = time.localtime()
    data_atual = (data_atual.tm_year - 1,data_atual.tm_mon)
    
    payload = flask.request.get_json()
    token = payload['token']

    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    atual = int(time.time())
    if atual > decode['duracao_token']:
        response = {'status':StatusCodes['api_error'],
                    'results':"tempo de sessão expirou"}
        conn.close()
        return flask.jsonify(response)

    if decode['permissao'] == "consumidor":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        conn.close()
        return flask.jsonify(response)
    
    try:
        data = time.strptime(data, "%Y-%m")
    except :
        response = {'status':StatusCodes['api_error'],
                    'results':'data não está no formato correto, o formato correto é do tipo YYYY-MM'}
        return flask.jsonify(response)    
# há aqui uma comparação entre um tuplo e um objeto do tipo data
    if data_atual > data:
        response = {'status':StatusCodes['api_error'],
                    'results': 'data limite um ano atrás'} 
        return flask.jsonify(response)

    statement =  """SELECT DATE_PART('month', historico_stream.data) AS mes, musica.genero, COUNT(*) AS total_streams
                    FROM historico_stream 
                    JOIN musica ON historico_stream.musica_ismn = musica.ismn
                    GROUP BY mes, musica.genero
                    HAVING DATE_PART('month',historico_stream.data) = %s -- porque não dá para utilizar mes aqui?
                    ORDER BY mes, total_streams DESC;
                    """
    
    cur.execute(statement,(data_atual[1],))
    val = cur.fetchall()
    if val == None:
        response = {'status':StatusCodes['api_error'],
                    'results':'não há registo de streams neste mes'}
        return flask.jsonify(response)

    logger.debug(val)
    response = {'status':StatusCodes['success'],'results':val}
    return flask.jsonify(response)


def hist_stream(data, ismn, user_id):
    conn = db_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN TRANSACTION")
        statement = "INSERT INTO historico_stream (data, musica_ismn, consumidor_utilizador_user_id) VALUES (%s, %s, %s)"
        values = (data, ismn, user_id)
        cur.execute(statement, values)
        conn.commit()
    except :
        conn.rollback()
    finally:
        if conn is not None:
            conn.close()
    return 


# ---------MOREIRA
def role(user_id):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM administrador WHERE utilizador_user_id = %s", user_id)
    if cur.fetchone():
        return "administrador"

    cur.execute("SELECT * FROM artista WHERE utilizador_user_id = %s", user_id)
    if cur.fetchone():
        return "artista"

    cur.execute(
        "SELECT * FROM consumidor WHERE utilizador_user_id = %s", user_id)
    if cur.fetchone():
        return "consumidor"


if __name__ == '__main__':

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.0 online: http://{host}:{port}')
