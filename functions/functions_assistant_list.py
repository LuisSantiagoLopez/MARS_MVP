# dic 17 -> arregla estas funciones y corre el bot 

scrapeUserWebsite = {
    "type": "function",
    "function": {
        "name": "scrapeUserWebsite",
        "description": "Escanea la página web del usuario para descubrir más sobre su negocio.",
        "parameters": {
            "type": "object",
            "properties": {
                "url_negocio": {"type": "string", "description": "El url del negocio del usuario."}
            },
            "required": ["url_negocio"]
        }
    }
}

searchInstagramTrends = {
    "type": "function",
    "function": {
        "name": "searchInstagramTrends",
        "description": "Descubre tendencias relevantes para el nicho del negocio del usuario en Instagram.",
        "parameters": {
            "type": "object",
            "properties": {
                "tres_palabras": {"type": "string", "description": "Tres palabras generales y comunes relacionadas con el negocio del usuario dentro de una lista en python."}
            },
            "required": ["tres_palabras"]
        }
    }
}

understandUserProduct = {
    "type": "function",
    "function": {
        "name": "understandUserProduct",
        "description": "Entiende el producto que el usuario quiere promocionar en su Instagram.",
        "parameters": {
            "type": "object",
            "properties": {
                "descripcion_negocio": {"type": "string", "description": "Una descripción del negocio del usuario."},
                "url": {"type": "string", "description": "El url de su foto de producto."}
            },
            "required": ["descripcion_negocio"]
        }
    }
}

generateInstagramImage = {
    "type": "function",
    "function": {
        "name": "generateInstagramImage",
        "description": "Genera la imagen que el usuario publicará en el Instagram de su negocio.",
        "parameters": {
            "type": "object",
            "properties": {
                "descripcion_negocio": {"type": "string", "description": "Una descripción del negocio del usuario. Incluye una descripción de su negocio y el estilo de imagen que el usuario especificó."},
                "idea": {"type": "string", "description": "La idea que el usuario aprobó."},
                "es_de_producto": {"type": "boolean", "description": "True si el usuario quiere una publicación promocional y False si quiere crear una publicación de entretenimiento; para que este valor sea True tuviste que correr la función understandUserProduct previamente.", "enum": ["True","False"]},
                "feedback": {"type": "string", "description": "El feedback que dio el usuario de las imágenes pasadas."}
            },
            "required": ["descripcion_negocio"]
        }
    }
}

generateInstagramCaption = {
    "type": "function",
    "function": {
        "name": "generateInstagramCaption",
        "description": "Genera la caption o leyenda que el usuario publicará junto con la imagen que aprobó al Instagram de su negocio.",
        "parameters": {
            "type": "object",
            "properties": {
                "descripcion_negocio": {"type": "string", "description": "Una descripción del negocio del usuario. Incluye una descripción de su negocio y el estilo de escritura que el usuario especificó."},
                "idea": {"type": "string", "description": "La idea que el usuario aprobó."},
                "descripcion_imagen": {"type": "string", "description": "Una descripción de la imagen que el usuario aprobó."},
                "feedback": {"type": "string", "description": "El feedback que dio el usuario de las captions pasadas."}
            },
            "required": ["descripcion_negocio"]
        }
    }
}

uploadInstagramImage = {
    "type": "function",
    "function": {
        "name": "uploadInstagramImage",
        "description": "Sube la publicación que generaste a Instagram.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_url": {"type": "string", "description": "El url de la imagen que el usuario aprobó."},
                "caption": {"type": "string", "description": "El caption que el usuario aprobó."},
                "usuario_instagram": {"type": "string", "description": "El nombre de usuario del Instagram del negocio del usuario."},
                "contraseña_instagram": {"type": "string", "description": "La contraseña del negocio del usuario."},
                "aprobacion_usuario": {"type": "boolean", "description": "True si el usuario otorgó su consentimiento explícito de publicar en su cuenta de Instagram.", "enum": ["True","False"]}
            },
            "required": ["image_url", "caption", "usuario_instagram", "contraseña_instagram", "aprobacion_usuario"]
        }
    }
}
