import asyncio

from sql_model.orm import create_table, drop_table, add


if __name__ == '__main__':
    asyncio.run(drop_table())
    asyncio.run(create_table())
    # asyncio.run(add())
