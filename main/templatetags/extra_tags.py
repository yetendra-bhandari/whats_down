from django import template
register = template.Library()
@register.filter
def starred_by(post, account):
    return post.starred_by.filter(id=account.id).exists()


@register.filter
def voted_by(comment, account):
    return comment.voted_by.filter(id=account.id).exists()
