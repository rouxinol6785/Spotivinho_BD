# tiago
import flask
import logging
import psycopg2
import jwt
import random

app = flask.Flask(__name__)
secret_key = '#FF8723#'
global token
token = ''

#verificação do token na payload
#commit antes de fechar
#não ha problema de funções a conectar novamente
#nova forma para as playlist
#criar os id todos da mesma forma
#meter a playlist na detail artist



StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}


def db_connection():
    db = psycopg2.connect(
        user = 'projeto_bd',
        password = 'password',
        host = '127.0.0.1',
        port = '5432',
        database = 'spotivinho_DB'
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



# registar novo consumidor
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
            #falta return
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

    logger.debug(f'POST /spotivinho_DB/user/artista - payload: {payload}')

    # verifica se é admin
    if token == '':
        response = {'status': StatusCodes['api-error'],
                    'results': 'Necessário admin para criar novo artista.'}
        return flask.jsonify(response)
    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    if decode['permissao'] == "administrador":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        return flask.jsonify(response)

    # verifica se está tudo na payload
    if "username" not in payload or " password" not in payload or "email" not in payload or "nome" not in payload or "idade" not in payload or "genero" not in payload or "nib" not in payload or "pais" not in payload or "data_nasc" not in payload or "label_label_id" not in payload:
        response = {
            'status': StatusCodes['api_error'], 'results': 'Missing required fields.'}

    # cria user id
    num_random = str(random.randint(0, 999999))
    user_id = f"{payload['username']}{num_random}"

    # querys a ser feitas
    statement = 'INSERT INTO utilizador (username,email,password,user_id) VALUES (%s, %s, %s, %s)'
    statement2 = 'INSERT INTO artista (nome,idade,nib,genero,pais,data_nasc,label_label_id,utilizador_user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'

    values = (payload['username'], payload['email'],
              payload['password'], user_id)
    values2 = (payload['nome'], payload['idade'], payload['nib'], payload['genero'],
               payload['pais'], payload['data_nasc'], payload['label_label_id'], user_id)

    try:

        cur.execute("SELECT * FROM utilizador WHERE username = %s",
                    (payload['username'],))
        existing_user = cur.fetchone()

        if existing_user:
            response = {
                'status': StatusCodes['api_error'], 'results': 'Username já existe!'}
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


# user login
@app.route('/spotivinho_DB/user/auth', methods=['PUT'])
def user_auth():
    global token
    logger.info('/spotivinho_DB/user/auth')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'PUT /spotivinho_DB/user/auth - payload: {payload}')

    if 'username' not in payload or 'password' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Insira password e username.'}
        return flask.jsonify(response)

    try:
        cur.execute("SELECT user_id FROM utilizador WHERE username = %s AND password = %s",
                    (payload['username'], payload['password']))
        existing_user = cur.fetchone()

        if existing_user:
            # verifica o tipo de utilizador, retorna uma string ("admin"/ "artista" / "consumidor")
            permissao = role(existing_user)
            print(str(existing_user))
            existing_user = str(existing_user).strip("(,')")

            # encodifica no token a permissao e user id de quem faz login
            payload["permissao"] = permissao
            payload["user_id"] = existing_user

            token = jwt.encode(payload, secret_key, algorithm='HS256')
            decode = jwt.decode(token,secret_key,algorithms=['HS256'])

            cur.execute("BEGIN TRANSACTION")

            response = {
                'status': StatusCodes['success'], 'results': f"{token} "}

        else:
            response = {
                'status': StatusCodes['api_error'], 'results': 'Credenciais incorretas.'} 
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



# adicionar musica cheka
@app.route('/spotivinho_DB/song', methods=['POST'])
def add_song():
    logger.info('POST /spotivinho_DB/song')
    payload = flask.request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'POST /spotivinho_DB/song - payload: {payload}')
    print(token)

    # verifica se é artista
    if token == '':
        response = {'status': StatusCodes['api_error'],
                    'results': 'Necessário ser artista para acicionar músicas.'}
        return flask.jsonify(response)
    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    if decode['permissao'] == "artista":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        return flask.jsonify(response)
    
    # falta um if para verificar se existe o campo outros artistas, de modo
    if "duracao" not in payload or "pub_data" not in payload or "genero" not in payload or "label_id" not in payload or "titulo" not in payload or "audio" not in payload or "album_album_id" not in payload:
        response = {
            'status': StatusCodes['api_error'], 'results': 'Missing required fields'}
        return flask.jsonify(response)

    statement = "INSERT into musica (ismn,duracao,pub_data,genero,label_id,titulo,audio,album_album_id,artista_utilizador_user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    num_random = str(random.randint(0, 999999))
    id = f"{payload['titulo']}{num_random}"

    try:
        decode = jwt.decode(token, secret_key, algorithms=['HS256'])
        artista_id = str(decode['user_id'])
        values = (id, payload["duracao"], payload["pub_data"], payload["genero"],
                  payload["label_id"], payload["titulo"], payload["audio"], payload["album_album_id"], artista_id)

        cur.execute("BEGIN TRANSACTION")
        cur.execute(statement, values)
        conn.commit()
        response = {
            'status': StatusCodes['success'], 'results': f'nova musica {payload["titulo"]} adicionada com sucesso!'}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /spotivinho_DB/song - error: {error}')
        response = {
            'status': StatusCodes['internal_error'], 'errors': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# ---------TIAGO
# detalhes artista
# neste momento só mostra todas as musicas e albuns da sua autoria
@app.route('/spotivinho_DB/artista_info/<artist_id>', methods=['GET'])
def detail_artist(artist_id):
    logger.info('GET /spotivinho_DB/artista_info/<artist_id>')

    logger.debug(f'artist_id: {artist_id}')

    conn = db_connection()
    cur = conn.cursor()

    statement = "SELECT artista.nome, musica.titulo, album.album_name, artista.data_nasc, artista.idade, artista.pais, artista.label_label_id FROM artista RIGHT JOIN musica ON artista.utilizador_user_id = musica.artista_utilizador_user_id RIGHT JOIN album ON artista.utilizador_user_id = album.artista_utilizador_user_id WHERE artista.utilizador_user_id = %s"

    try:

        cur.execute(statement, (artist_id,))
        rows = cur.fetchall()

        logger.debug(rows)
        Results = []
        content = {
                    'Artista': rows[0][0],
                    'Data nascimento': rows[0][3],
                    'Idade': rows[0][4],
                    'Pais': rows[0][5],}
        Results.append(content)
        for row in rows:
            logger.debug(row)
            content = {
                       'Musicas': row[1],  # nome ou id??
                       'Albuns': row[2],
                       # falta meter playlist!!!!!!!!!!!!!!
                       'Label': row[6]
                       }
            Results.append(content)
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


# ---------MOREIRA
# adicionar pre-paid card
@app.route('/spotivinho_DB/card', methods=['POST'])
def add_card():
    logger.info('POST /spotivinho_DB/card')

    conn = db_connection()
    cur = conn.cursor()

    payload = flask.request.get_json()

    logger.debug(f'POST /spotivinho_DB/card - payload: {payload}')

    # verifica se é admin
    if token == '':
        response = {'status': StatusCodes['api_error'],
                    'results': 'Necessário ser admin para criar pre-paid cards.'}
        return flask.jsonify(response)
    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    if decode['permissao'] == "administrador":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        return flask.jsonify(response)

    # verifica se todos os campos necessários estão na payload
    if "valor" not in payload or "expiration_date" not in payload or "quantidade" not in payload:
        response = {
            'status': StatusCodes['api_error'], 'results': 'Missing required fields.'}
        return flask.jsonify(response)

    if int(payload['valor'])not in (10, 25, 50):
        response = {'status': StatusCodes['api_error'],
                    'results': 'valor dos pre_paid_cards tem que ser 10, 25 ou 50.'}
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
                'status': StatusCodes['success'], 'results': f"{payload['quantidade']} pre-paid cards adicionados no valor de {payload['valor']}, com os ids {ids}!"}
        else:
            response = {
                'status': StatusCodes['success'], 'results': f"{payload['quantidade']} pre-paid card adicionado  no valor de {payload['valor']}, com o id{ids[0]}!"}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'POST /spotivinho_DB/card - error: {error}')
        response = {
            'status': StatusCodes['internal_error'], 'errors': str(error)}

        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return flask.jsonify(response)


# search_song
@app.route('/spotivinho_DB/song/<titulo>', methods=['GET'])
def search_song(titulo):
    logger.info('GET /spotivinho_DB/song/<titulo>')

    logger.debug(f'titulo: {titulo}')

    conn = db_connection()
    cur = conn.cursor()
    print(titulo)
    var = '%'
    statement = "SELECT musica.titulo, artista.nome, album.album_name, musica.outros_artistas, musica.genero, musica.duracao FROM musica INNER JOIN artista ON musica.artista_utilizador_user_id = artista.utilizador_user_id INNER JOIN album ON musica.album_album_id = album.album_id WHERE musica.titulo LIKE %s || %s || %s"

    try:
        cur.execute(statement, (var, titulo,var))
        rows = cur.fetchall()
        Results = []

        for row in rows:
            logger.debug(row)
            content = {'titulo':             row[0],
                       'artistas':           row[1],
                       'album':              row[2],
                       'artistas_associados': row[3],
                       'genero':             row[4],
                       'duracao':            row[5]
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


# adiconar_album, falta criar album id, bora pensar numa boa forma para fazer todos os ids
@app.route('/spotivinho_DB/album', methods=['POST'])
def add_album():
    logger.info('POST /spotivinho_DB/album')

    # tou a pensar isto deveria ser sempre a primeira coisa, não deve fazer nada antes de verificar se tem autorização, certo?
    # verifica se é artista
    if token == '':
        response = {'status': StatusCodes['api_error'],
                    'results': 'Necessário ser artista para acicionar albuns.'}
        return flask.jsonify(response)
    decode = jwt.decode(token, secret_key, algorithms=['HS256'])
    if decode['permissao'] == "artista":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        return flask.jsonify(response)

    conn = db_connection()
    cur = conn.cursor()

    payload = flask.request.get_json()
    if 'tracklist' not in payload or 'titulo' not in payload or 'duracao' not in payload or 'pub_data' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Missing required fields'}
        return flask.jsonify(response)
    logger.debug(f'POST /spotivinho_DB/album - payload: {payload}')
    num_random = str(random.randint(0, 999999))
    id = f"{payload['titulo']}{num_random}"
    statement = "Select * from musica where ismn = %s"
    statement4 = "Select * from album where album_id = %s"
    statement2 = "INSERT into musica (ismn,duracao,pub_data,genero,label_id,titulo,audio,album_album_id,artista_utilizador_user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    statement3 = "INSERT into album (album_id,tracklist,titulo,duracao,artista_utilizador_user_id,pub_data) VALUES (%s,%s,%s,%s,%s,%s)"
    values = (id, payload['tracklist'], payload['titulo'],
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
            if len(musica) < 6:
                response = {
                    'status': StatusCodes['api_error'], 'results': f'missing required fields in musica{musica[5]}'}
                return flask.jsonify(response)

            # isto só é necessário para selects, nos inserts dá merda
            cur.execute(statement, (musica[0],))
            # verifica se a música existe
            if cur.fetchone():
                pass
            else:
                values = (musica[0], musica[1], musica[2], musica[3], musica[4],
                          musica[5], musica[6], payload['album_id'], decode['user_id'])
                # adiciona à base de dados
                cur.execute(statement2, values)
                novidades = novidades + "- " + musica[5] + "\n"

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


# create playlist
@app.route('/spotivinho_DB/playlist', methods=['POST'])
def add_playlist():
    logger.info('POST /spotivinho_DB/playlist')

    if token == '':
        response = {'status': StatusCodes['api_error'],
                    'results': 'Necessário ser consumidor premium para adiciondar playlist.'}
        return flask.jsonify(response)

    decode = jwt.decode(token, secret_key, algorithms=['HS256'])

    if decode['permissao'] == "consumidor":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        return flask.jsonify(response)

    statement = "SELECT status FROM consumidor WHERE utilizador_user_id = %s"
    statement1 = "SELECT * FROM musica WHERE ismn = %s"
    statement2 = "INSERT INTO playlist (playlist_id,titulo,tracklist,duracao,descricao,consumidor_utilizador_user_id,visibility ) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    values = decode['user_id']

    conn = db_connection()
    cur = conn.cursor()

    payload = flask.request.get_json()
    logger.debug(f'POST /spotivinho_DB/playlist - payload: {payload}')

    if 'titulo' not in payload or 'tracklist' not in payload or 'duracao' not in payload or 'descricao' not in payload or 'visibility' not in payload:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Missing required fields'}
        return flask.jsonify(response)

    tracklist = payload['tracklist'].split(",")

    try:
        cur.execute(statement, (values,))
        status = cur.fetchone()
        status = status[0]

        # check status
        if status == 'regular':
            response = {'status': StatusCodes['api_error'],
                        'results': 'utilizador tem que ser premium para criar playlists!'}
            return flask.jsonify(response)

        # check visibility
        if payload['visibility'] != 'private' and payload['visibility'] != 'public':
            response = {'status': StatusCodes['api_error'],
                        'results': 'visibility só pode ser public ou private'}
            return flask.jsonify(response)

        # check se todos os id estão na tabela música
        for item in tracklist:
            values = item
            cur.execute(statement1, (values,))
            if cur.fetchone():
                pass
            else:
                response = {'status': StatusCodes['api_error'],
                            'results': f'a música com o id - {item} não está presente na base de dados.'}
                return flask.jsonify(response)

        playlist_id = "@" + payload['titulo']
        values = (playlist_id, payload['titulo'], payload['tracklist'], payload['duracao'],
                  payload['descricao'], decode['user_id'], payload['visibility'])

        # insere a playlist em playlist
        cur.execute(statement2, values)
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


#play song
@app.route('/spotivinho_DB', methods = ['PUT'])
def play_song():
    logger.info('POST /spotivinho_DB/playlist')

    if token == '':
        response = {'status': StatusCodes['api_error'],
                    'results': 'sessão iniciada para tocar musica por favor!.'}
        return flask.jsonify(response)

    decode = jwt.decode(token, secret_key, algorithms=['HS256'])

    if decode['permissao'] == "consumidor":
        pass
    else:
        response = {'status': StatusCodes['api_error'],
                    'results': 'Utilizador não tem permissão.'}
        return flask.jsonify(response)

# ---------MOREIRA
# conectar 2 vezes na base de dados?
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
