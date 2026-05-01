from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.blog_post import BlogPost
from app.models.social_post import SocialPost

logger = get_logger(__name__)


def build_facebook_copy(post: BlogPost) -> str:
    return f"{post.title}\n\nLee mas en nuestro blog: /blog/{post.slug}"


def build_instagram_copy(post: BlogPost) -> str:
    return f"{post.title}\n\n#noticias #actualidad"


def publish_social_posts(db: Session) -> dict:
    logger.info("Community manager iniciado")

    try:
        blog_posts = db.query(BlogPost).all()
        created_social_posts = 0

        for post in blog_posts:
            # FACEBOOK
            existing_facebook = (
                db.query(SocialPost)
                .filter(
                    SocialPost.blog_post_id == post.id,
                    SocialPost.platform == "facebook",
                )
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

            # INSTAGRAM
            existing_instagram = (
                db.query(SocialPost)
                .filter(
                    SocialPost.blog_post_id == post.id,
                    SocialPost.platform == "instagram",
                )
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

        logger.info(
            "Community manager finalizado | blog_posts_processed=%s social_posts_created=%s",
            len(blog_posts),
            created_social_posts,
        )

        return {
            "status": "ok",
            "blog_posts_processed": len(blog_posts),
            "social_posts_created": created_social_posts,
        }

    except Exception as exc:
        db.rollback()
        logger.exception("Community manager fallo: %s", exc)

        return {
            "status": "error",
            "error": str(exc),
            "blog_posts_processed": 0,
            "social_posts_created": 0,
        }