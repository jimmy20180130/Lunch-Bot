import pygsheets
import json
import discord
from discord.ext import commands
import os
from discord_webhook import DiscordWebhook, DiscordEmbed
import asyncio
import time
import schedule

with open("settings.json", "r", encoding='utf-8') as settings:
    setting = json.load(settings)

# 取得lunch.json的資料
with open("lunch.json", "r", encoding='utf-8') as lunch_file:
    lunch_data = json.load(lunch_file)

# 取得user.json的資料
with open("user.json", "r") as user_file:
    user_data = json.load(user_file)

def count_lunch_items():
    lunch_counts = {lunch_data[lunch_id]["name"]: 0 for lunch_id in lunch_data}

    for user_id, data in user_data.items():
        lunch_id = data["lunch"]
        if lunch_id in lunch_data:
            lunch_name = lunch_data[lunch_id]["name"]
            lunch_counts[lunch_name] += 1

    lunch_counts_list = [(count, lunch_name) for lunch_name, count in lunch_counts.items()]
    lunch_counts_list.sort(reverse=True)  # Sort by count in descending order

    return lunch_counts_list

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=setting['prefix'], intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'機器人已上線({bot.user})')
    await start_timer()

@bot.command()
@commands.is_owner()
async def load_sheet(ctx):
    await ctx.send('已開始讀取最新資料')
    process_orders(load_sheet())
    await ctx.send('已完成讀取資料')

@bot.command()
@commands.is_owner()
async def set_money(ctx, user :int, money :int):
    user_id = str(user)
    if user_id in user_data:
        user_data[user_id]['wallet'] = money
        with open('user.json', 'w') as user_file:
            json.dump(user_data, user_file, indent=4)
        await ctx.send(f"{user_id}號的錢包已設為了{money}元\n目前有{user_data[user_id]['wallet']}元")

@bot.command()
@commands.is_owner()
async def add_money(ctx, user :int, money :int):
    user_id = str(user)
    if user_id in user_data:
        user_data[user_id]['wallet'] += money
        with open('user.json', 'w') as user_file:
            json.dump(user_data, user_file, indent=4)
        await ctx.send(f"{user_id}號的錢包新增了{money}元\n目前有{user_data[user_id]['wallet']}元")

@bot.command()
@commands.is_owner()
async def remove_money(ctx, user :int, money :int):
    user_id = str(user)
    if user_id in user_data:
        user_data[user_id]['wallet'] -= money
        with open('user.json', 'w') as user_file:
            json.dump(user_data, user_file, indent=4)
        await ctx.send(f"{user_id}號的錢包移除了{money}元\n目前有{user_data[user_id]['wallet']}元")

@bot.command()
@commands.is_owner()
async def add_flavor(ctx, flavor :str, price :int):
    lunch_data[str(len(lunch_data) + 1)] = {
        'name': flavor,
        'price': price
    }
    with open('lunch.json', 'w') as lunch_file:
        json.dump(lunch_data, lunch_file, indent=4)
    await ctx.send(f"已新增項目: {flavor}\n價錢為{price}元")

@bot.command()
@commands.is_owner()
async def remove_flavor(ctx, flavor :str):
    for key, value in lunch_data.items():
        if value['name'] == flavor:
            lunch_data.pop(key)
            with open('lunch.json', 'w') as lunch_file:
                json.dump(lunch_data, lunch_file, indent=4)
            await ctx.send(f"Removed flavor: {flavor}")
            # 取得lunch.json的資料
            with open("lunch.json", "r", encoding='utf-8') as lunch_file:
                lunch_data = json.load(lunch_file)

            # 取得user.json的資料
            with open("user.json", "r") as user_file:
                user_data = json.load(user_file)
            return
    await ctx.send(f"無法找到項目: {flavor}")

@bot.command()
@commands.is_owner()
async def set_flavor(ctx, flavor: str, price: int):
    for key, value in lunch_data.items():
        if value['name'] == flavor:
            value['price'] = str(price)
            with open('lunch.json', 'w') as lunch_file:
                json.dump(lunch_data, lunch_file, indent=4)
            await ctx.send(f"Set price for flavor {flavor} to {price}")
            # 取得lunch.json的資料
            with open("lunch.json", "r", encoding='utf-8') as lunch_file:
                lunch_data = json.load(lunch_file)

            # 取得user.json的資料
            with open("user.json", "r") as user_file:
                user_data = json.load(user_file)
            return
    await ctx.send(f"無法找到項目: {flavor}")

@bot.command()
@commands.is_owner()
async def clear_lunch(ctx, user_id :int):
    user_data[str(user_id)]['lunch'] = ''
    with open('user.json', 'w', encoding='utf-8') as user_file:
        json.dump(user_data, user_file, ensure_ascii=False, indent=4)
    await ctx.send(f'已將{user_id}的午餐清空')

@bot.command()
@commands.is_owner()
async def clear_all_lunch(ctx):
    for user in user_data:
        user_data[user]['lunch'] = ''
    with open('user.json', 'w', encoding='utf-8') as user_file:
        json.dump(user_data, user_file, ensure_ascii=False, indent=4)
    await ctx.send(f'已將所有人的午餐清空')

@bot.command()
@commands.is_owner()
async def add_discord(ctx, user_id :int, discord_id :int):
    user_data[str(user_id)]['discord_id'] = discord_id
    with open('user.json', 'w', encoding='utf-8') as user_file:
        json.dump(user_data, user_file, ensure_ascii=False, indent=4)
    await ctx.send(f'{user_id}號的帳號已與<@{discord_id}>連結')
    # 取得lunch.json的資料
    with open("lunch.json", "r", encoding='utf-8') as lunch_file:
        lunch_data = json.load(lunch_file)

    # 取得user.json的資料
    with open("user.json", "r") as user_file:
        user_data = json.load(user_file)

@bot.command()
@commands.is_owner()
async def count_lunch(ctx):
    # 取得lunch.json的資料
    with open("lunch.json", "r", encoding='utf-8') as lunch_file:
        lunch_data = json.load(lunch_file)

    # 取得user.json的資料
    with open("user.json", "r") as user_file:
        user_data = json.load(user_file)
    webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1143563857797849260/xCaTsRsc7SGOv1PejwjD-yZDSqMQnKBzGOQ_hKrndZl05J396h53nf6ooSAJNSvuir_G")
    embed = DiscordEmbed(title="午餐統計", color=0x03b2f8)
    for count, lunch_name in count_lunch_items():
        embed.add_embed_field(name=lunch_name, value=str(count), inline=False)
    # add embed object to webhook
    webhook.add_embed(embed)
    response = webhook.execute()

def load_sheet():
    # 認證+讀取google sheet
    gc = pygsheets.authorize(service_file='credentials.json')
    spreadsheet = gc.open('lunch')
    worksheet_name = 'lunch'  # 工作表名稱
    worksheet = spreadsheet.worksheet_by_title(worksheet_name)

    #取得所有非空白格
    all_values = worksheet.get_all_values()

    # 找到有數值的最後一行的資料
    last_row_index = None
    for idx, row in reversed(list(enumerate(all_values))):
        if any(cell_value for cell_value in row):
            last_row_index = idx
            break

    if last_row_index is not None:
        # 取得從第二行到最後一個有數值的行(三列)
        data_range = [[row[i] for i in range(3) if i < len(row) and row[i]] for row in all_values[1:last_row_index + 1]]
        # 将 previous_data 字符串转换为列表
        previous_data = setting['previous_data']

        # 比較
        data_set = {tuple(data) for data in data_range}
        previous_data_set = {tuple(data) for data in previous_data}
        print(data_set, previous_data_set)

        # 找到新增的資料
        different_data = data_set.difference(previous_data_set)
        print(different_data)

        # 轉成列表
        different_data_list = [list(data) for data in different_data]
        print(different_data_list)

        # 更新 setting 中的 previous_data
        setting['previous_data'] = [list(data) for data in data_set]

        # 寫回settings.json
        with open('settings.json', 'w', encoding='utf-8') as settings_file:
            json.dump(setting, settings_file, ensure_ascii=False, indent=4)

        return different_data_list
    else:
        print("no data")
        return "no data"
    
def save_user_data():
    with open("user.json", "w") as user_file:
        json.dump(user_data, user_file, indent=4)

def get_lunch_id(lunch_name):
    lunch_id = "1"
    for lunch_id in lunch_data:
        if lunch_data[lunch_id]['name'] == lunch_name:
            break
        else:
            lunch_id_int = int(lunch_id)
            lunch_id_int += 1
            lunch_id = str(lunch_id_int)
    return lunch_id

def add_order(user_id, lunch_id):
    user_data[user_id] = {
        "discord_id": user_id,
        "wallet": str(int(user_data[user_id]["wallet"]) - int(lunch_data[lunch_id]["price"])),
        "lunch": lunch_id
    }
    save_user_data()

def update_order(user_id, lunch_id):
    previous_lunch_id = user_data[user_id]["lunch"]
    if user_data[user_id]["lunch"] != '':
        save_user_data()
        return previous_lunch_id
    else:
        save_user_data()
        return 'a'

def process_orders(orders):
    for order in orders:
        webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1143563857797849260/xCaTsRsc7SGOv1PejwjD-yZDSqMQnKBzGOQ_hKrndZl05J396h53nf6ooSAJNSvuir_G")
        user_id = order[1]
        member_id = user_data[user_id]['discord_id']
        lunch_id = get_lunch_id(order[2])
        if user_id in user_data:
            if user_data[user_id]["lunch"] != lunch_id:
                if lunch_id in lunch_data:
                    if int(user_data[user_id]["wallet"]) >= int(lunch_data[lunch_id]["price"]):
                        lunch_return = update_order(user_id, lunch_id)
                        if lunch_return == 'a':
                            user_data[user_id]["lunch"] = lunch_id
                            user_data[user_id]["wallet"] = int(user_data[user_id]["wallet"]) - int(lunch_data[lunch_id]["price"])
                            save_user_data()
                            embed = DiscordEmbed(title="新增午餐", color="03b2f8")
                            if user_data[user_id]['discord_id'] != '':
                                embed.add_embed_field(name="用戶", value=f'<@{member_id}>', inline=False)
                            else:
                                embed.add_embed_field(name="用戶", value=f'{user_id}', inline=False)
                            embed.add_embed_field(name="午餐", value=lunch_data[lunch_id]["name"], inline=False)
                            embed.add_embed_field(name="花費", value=f'{lunch_data[lunch_id]["price"]}元', inline=False)
                            embed.add_embed_field(name="餘額", value=f'{user_data[user_id]["wallet"]}元', inline=False)
                            # add embed object to webhook
                            webhook.add_embed(embed)
                            response = webhook.execute()
                        else:
                            user_data[user_id]["lunch"] = lunch_id
                            user_data[user_id]["wallet"] = int(user_data[user_id]["wallet"]) - int(lunch_data[lunch_id]["price"])
                            save_user_data()
                            previous_lunch_id = lunch_return
                            # create embed
                            embed = DiscordEmbed(title="更改午餐", color="03b2f8")
                            if user_data[user_id]['discord_id'] != '':
                                embed.add_embed_field(name="用戶", value=f'<@{member_id}>', inline=False)
                            else:
                                embed.add_embed_field(name="用戶", value=f'{user_id}', inline=False)
                            embed.add_embed_field(name="午餐", value=lunch_data[previous_lunch_id]["name"] + '->' + lunch_data[lunch_id]["name"], inline=False)
                            embed.add_embed_field(name="花費", value=f'{lunch_data[lunch_id]["price"]}元', inline=False)
                            embed.add_embed_field(name="餘額", value=f'{user_data[user_id]["wallet"]}元', inline=False)
                            # add embed object to webhook
                            webhook.add_embed(embed)
                            response = webhook.execute()
                    else:
                        print(f"{user_id}無足夠的餘額")
                        embed = DiscordEmbed(title="無足夠餘額", color="03b2f8")
                        if user_data[user_id]['discord_id'] != '':
                            embed.add_embed_field(name="用戶", value=f'<@{member_id}>', inline=False)
                        else:
                            embed.add_embed_field(name="用戶", value=f'{user_id}', inline=False)
                        embed.add_embed_field(name="午餐", value=lunch_data[lunch_id]["name"], inline=False)
                        # add embed object to webhook
                        webhook.add_embed(embed)
                        response = webhook.execute()
                else:
                    print(f"{user_id}無效的午餐ID")
                    embed = DiscordEmbed(title="無效的午餐ID", color="03b2f8")
                    if user_data[user_id]['discord_id'] != '':
                        embed.add_embed_field(name="用戶", value=f'<@{member_id}>', inline=False)
                    else:
                        embed.add_embed_field(name="用戶", value=f'{user_id}', inline=False)
                    embed.add_embed_field(name="午餐", value=lunch_id, inline=False)
                    # add embed object to webhook
                    webhook.add_embed(embed)
                    response = webhook.execute()
            else:
                print(f"{user_id}已點過此品項")
                embed = DiscordEmbed(title="已點過品項", color="03b2f8")
                if user_data[user_id]['discord_id'] != '':
                    embed.add_embed_field(name="用戶", value=f'<@{member_id}>', inline=False)
                else:
                    embed.add_embed_field(name="用戶", value=f'{user_id}', inline=False)
                embed.add_embed_field(name="午餐", value=lunch_data[lunch_id]["name"], inline=False)
                # add embed object to webhook
                webhook.add_embed(embed)
                response = webhook.execute()

def start_scheduler():
    # Schedule the count_lunch_items function to run daily at 4:00 PM
    schedule.every().day.at("16:00").do(count_lunch_items)

    # Run the scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)

async def start_timer():
    while True:
        now_data = load_sheet()
        if now_data != ([] or 'no data'):
            process_orders(now_data)
        await asyncio.sleep(600)  # 等待 600 秒（10 分鐘）

if __name__ == "__main__":
    bot.run(setting['bot_token'])
    start_scheduler()