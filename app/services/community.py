from sqlalchemy.orm import Session

from app.models.blog_post import BlogPost
from app.models.social_post import SocialPost


def build_facebook_copy(post: BlogPost) -> str:
    return f"{post.title}\n\nLee más en nuestro blog: /blog/{post.slug}"


def build_instagram_copy(post: BlogPost) -> str:
    return f"{post.title}\n\nMás detalles en nuestro blog.\n#noticias #chile #actualidad"


def publish_social_posts(db: Session) -> dict:
    blog_posts = db.query(BlogPost).all()

    created_social_posts = 0

    for post in blog_posts:
        existing_facebook = (
            db.query(SocialPost)
            .filter(SocialPost.blog_post_id == post.id, SocialPost.platform == "facebook")
            .first()
        )

        if not existing_facebook:
            db.add(
                SocialPost(
                    blog_post_id=post.id,
                    platform="facebook",
                    post_copy=build_facebook_copy(post),
                    status="published",
                )
            )
            created_social_posts += 1

        existing_instagram = (
            db.query(SocialPost)
            .filter(SocialPost.blog_post_id == post.id, SocialPost.platform == "instagram")
            .first()
        )

        if not existing_instagram:
            db.add(
                SocialPost(
                    blog_post_id=post.id,
                    platform="instagram",
                    post_copy=build_instagram_copy(post),
                    status="published",
                )
            )
            created_social_posts += 1

    db.commit()

    return {
        "status": "ok",
        "blog_posts_processed": len(blog_posts),
        "social_posts_created": created_social_posts,
    }