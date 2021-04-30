async def is_admin(ctx):
  return ctx.message.author.server_permissions.administrator