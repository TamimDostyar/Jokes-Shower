from flask import Flask, jsonify, abort
import pyjokes
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

LANGUAGES = {
    "cs": "Czech",
    "de": "German",
    "en": "English",
    "es": "Spanish",
    "eu": "Basque",
    "fr": "French",
    "gl": "Galician",
    "hu": "Hungarian",
    "it": "Italian",
    "lt": "Lithuanian",
    "pl": "Polish",
    "sv": "Swedish",
}

CATEGORIES = ["all", "neutral", "chuck"]
joke_generator = pyjokes.get_jokes


@app.route("/")
def dummy():
    return jsonify(message="Try the endpoint")


@app.route("/api/v1/jokes/<language>/<category>", methods=["GET"])
@app.route("/api/v1/jokes/<language>/<category>/<int:num>", methods=["GET"])
def get_all_jokes(language, category, num=None):
    """Get all jokes or a specified number of jokes."""
    if language not in LANGUAGES:
        abort(404, description=f"404 Not Found: Language {language} does not exist.")

    if category not in CATEGORIES:
        abort(404, description=f"404 Not Found: Category {category} does not exist.")

    try:
        jokes = joke_generator(language=language, category=category)
        if not jokes:
            abort(
                404,
                description=f"No jokes found for language '{language}' in category '{category}'.",
            )
    except Exception as e:
        abort(
            404,
            description=f"There are no {category} jokes in {LANGUAGES.get(str(language))}",
        )

    if num is not None:
        return get_n_jokes(language, category, num)

    return jsonify({"jokes": jokes})


def get_n_jokes(language, category, number):
    """Fetch n jokes from the list of jokes."""
    jokes = pyjokes.get_jokes(language=language, category=category)
    return jsonify({"jokes": jokes[:number]})


@app.route("/api/v1/jokes/<int:joke_id>", methods=["GET"])
def get_the_joke(joke_id):
    """Fetch a single joke based on the joke_id."""
    all_jokes = []

    for language in LANGUAGES.keys():
        try:
            jokes = joke_generator(language=language, category="all")
            all_jokes.extend(jokes)
        except Exception:
            continue

    if joke_id < 0 or joke_id >= len(all_jokes):
        abort(
            404,
            description=f"Joke {joke_id} not found, try an id between 0 and {len(all_jokes) - 1}",
        )

    joke = all_jokes[joke_id]
    return jsonify({"jokes": joke})


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error)}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
