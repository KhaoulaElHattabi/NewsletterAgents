NEWSLETTER_TEMPLATE = """ 
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GenAI Info est là - Votre newsletter hebdomadaire</title>
<style>
    body {
        font-family: Arial, sans-serif;
        font-size: 16px;
        margin: 0;
        padding: 0;
        color: #333;
    }
    .newsletter-container {
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
    }
    .article-summary {
        margin-bottom: 30px;
    }
    .article-summary h2 {
        font-size: 20px;
        color: #0073AA;
    }
    .article-summary p {
        margin: 0;
        color: #666;
    }
    .article-summary a {
        color: #0073AA;
        text-decoration: none;
    }
    .header-image {
        width: 100%;
        max-width: 600px;
        height: auto;
        display: block;
        margin: 0 auto 20px;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        font-size: 14px;
    }
    .footer p {
        margin: 0;
    }
</style>
</head>
<body>
<div class="newsletter-container">
<h1>&#x1F4F0; GenAI Info est là - Votre newsletter hebdomadaire &#x1F4F0;</h1>

<p>{{introduction}}</p>

{{article_summaries}}

<div class="footer">
    <p>{{conclusion}}</p>
</div>

</div>
</body>
</html>

Instructions for filling the template:
1. Replace {{introduction}} with an engaging introduction in French.
2. Replace {{article_summaries}} with the summaries of the articles. For each article, use the following structure:

<div class="article-summary">
    <h2>&#x1F4A1; {{article_title}}</h2>
    <p>{{article_summary}}</p>
    <a href="{{article_link}}" target="_blank">Lire l'article complet</a>
</div>
"""