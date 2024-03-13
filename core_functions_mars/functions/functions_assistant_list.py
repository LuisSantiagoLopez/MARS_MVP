scrapeUserWebsiteFunclist = {
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

searchInstagramTrendsFunclist = {
    "type": "function",
    "function": {
        "name": "searchInstagramTrends",
        "description": "Encuentra y analiza publicaciones del nicho del usuario con más de 50 me gusta en instagram.",
        "parameters": {
            "type": "object",
            "properties": {
                "palabra": {"type": "string", "description": """Una palabra popular en redes sociales sin acentos que represente el negocio del usuario."""}
            },
            "required": ["palabra"]
        }
    }
}

understandUserProductFunclist = {
    "type": "function",
    "function": {
        "name": "understandUserProduct",
        "description": "Puedes ver el producto del usuario y entenderlo.",
        "parameters": {
            "type": "object",
            "properties": {
                "descripcion_negocio": {"type": "string", "description": "Una descripción del negocio del usuario."},
            },
            "required": []
        }
    }
}

generateInstagramImageFunclist = {
    "type": "function",
    "function": {
        "name": "generateInstagramImage",
        "description": "Genera la imagen que el usuario publicará en el Instagram de su negocio.",
        "parameters": {
            "type": "object",
            "properties": {
                "descripcion_negocio": {"type": "string", "description": "Una descripción del negocio del usuario. Incluye una descripción de su negocio y el estilo de imagen que el usuario especificó."},
                "idea": {"type": "string", "description": "La idea de la imagen a generar."},
                "es_de_producto": {"type": "boolean", "description": "True si el usuario quiere una publicación promocional y False si quiere crear una publicación de entretenimiento; Si utilizaste la función understandUserProduct previamente, y el usuario quiere hacer una publicación de su producto, indica True.", "enum": ["True","False"]},
                "estilo": {"type": "string", "description": "El estilo del negocio, si no lo cononoces intúyelo."},
                "feedback": {"type": "string", "description": "El feedback que dio el usuario de las imágenes pasadas."}
            },
            "required": ["idea"]
        }
    }
}

generateInstagramCaptionFunclist = {
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
                "feedback": {"type": "string", "description": "El feedback que dio el usuario de las captions pasadas."},
                "estilo": {"type":"string", "description": "Estilo de escritura del negocio, si no lo especificó intúyelo."}
            },
            "required": ["idea"]
        }
    }
}

uploadInstagramImageFunclist = {
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
