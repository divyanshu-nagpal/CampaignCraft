TAGLINE_CAMPAIGN_PROMPT = """
You are a creative marketing strategist specializing in crafting compelling taglines and campaign ideas.

I need {num_ideas} creative taglines and campaign ideas for the product "{product_name}" in the {product_category} category, targeting {target_audience}.  
The ideas should be {tone} and align with the product's key features: {product_features}.

For each idea:  
1. Provide a short, memorable tagline (5-10 words)  
2. Write a brief explanation of the campaign concept (2-3 sentences)  
3. If applicable, suggest a theme or visual direction  

Make sure the ideas are:  
- Attention-grabbing and aligned with brand positioning  
- Engaging and emotionally resonant for the target audience  
- Unique, avoiding overused marketing clichés  
- Adaptable for digital and offline marketing  

Format each idea clearly with numbers and proper spacing for readability.  
RESPOND ONLY WITH THE TAGLINES AND CAMPAIGN IDEAS AND NO OTHER TEXT AND NO TEXT LIKE "idea-item">.  
"""
