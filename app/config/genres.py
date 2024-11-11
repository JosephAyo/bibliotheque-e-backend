from ..database.base import SessionLocal
from ..repository import genre as genre_repository
from ..schemas import genre as genre_schemas
from faker import Faker


fake = Faker()

default_genres = [
    {
        "name": "Fiction",
        "description": "Narrative works created from the imagination of the author.",
    },
    {
        "name": "Non-Fiction",
        "description": "Factual works based on real events, people, or places.",
    },
    {
        "name": "Poetry",
        "description": "Literary work in which special intensity is given to the expression of feelings and ideas by the use of distinctive style and rhythm.",
    },
    {
        "name": "Drama",
        "description": "A composition in verse or prose intended to portray life or character or tell a story usually involving conflicts and emotions through action and dialogue and typically designed for theatrical performance.",
    },
    {
        "name": "Science Fiction",
        "description": "A genre of speculative fiction that typically deals with futuristic settings and technology.",
    },
    {
        "name": "Fantasy",
        "description": "A genre of literature that uses magic and other supernatural phenomena as primary elements of its plot, theme, setting, or atmosphere.",
    },
    {
        "name": "Mystery",
        "description": "A genre of fiction in which a detective or other character investigates a puzzling crime.",
    },
    {
        "name": "Horror",
        "description": "A genre of fiction that seeks to elicit feelings of fear, dread, and disgust.",
    },
    {
        "name": "Romance",
        "description": "A genre of literature that involves stories of love and romantic relationships.",
    },
    {
        "name": "Historical Fiction",
        "description": "A genre of fiction that incorporates historical figures and events into a fictional narrative.",
    },
    {
        "name": "Dystopian",
        "description": "A genre of fiction that presents a futuristic society in which conditions of life are extremely bad and oppressive.",
    },
    {
        "name": "Utopian",
        "description": "A genre of fiction that presents an idealized vision of a society.",
    },
]


def create_default_genres():
    genre_count = genre_repository.count_all(SessionLocal())
    if genre_count >= len(default_genres):
        return
    for genre in default_genres:
        genre_repository.create(
            genre_schemas.CreateGenre(**genre),
            SessionLocal(),
        )
