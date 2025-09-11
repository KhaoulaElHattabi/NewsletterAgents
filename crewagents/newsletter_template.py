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
        background-color: #f4f4f4;
    }
    .newsletter-container {
        width: 90%;
        max-width: 600px;
        margin: 20px auto;
        padding: 20px;
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .article-summary {
        margin-bottom: 30px;
        text-align: left;
    }
    .article-summary h2 {
        font-size: 20px;
        color: #0073AA;
    }
    .article-summary p {
        margin: 10px 0;
        color: #666;
    }
    .header-image {
        width: 100%;
        max-width: 600px;
        height: auto;
        display: block;
        margin: 0 auto 20px;
    }

    .article-summary a {
        color: #0073AA;
        text-decoration: none;
        display: inline-block;
        margin-top: 5px;
    }
    .header-image {
        width: 100%;
        max-width: 600px;
        height: auto;
        display: block;
        margin: 0 auto 20px;
    }
    h1 {
        text-align: center;
        color: #0073AA;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        font-size: 14px;
    }
    .footer p {
        margin: 0;
        color: #666;
    }
</style>
</head>
<body>
<div class="newsletter-container">
<img src="cid:Mailtrapimage" alt="Newsletter Image" class ="header-image">
<h1>&#x1F4F0; GenAI Info est là - Newsletter hebdomadaire - Semaine {{week_number}} &#x1F4F0;</h1>

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
