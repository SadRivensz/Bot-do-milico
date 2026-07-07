"""
Live ON — Bot de recrutamento
Equivalente Python do bot TypeScript.

Dependências:
    pip install discord.py

Variáveis de ambiente necessárias:
    DISCORD_BOT_TOKEN      — token do bot
    TICKETTOOL_BOT_ID      — ID do bot TicketTool (padrão: 557628352828014614)
"""

import discord
import logging
import os
import re

# ─── Lê .env se existir (sem precisar instalar python-dotenv) ────────────────

def _load_env(path: str = ".env") -> None:
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except FileNotFoundError:
        pass  # .env opcional

_load_env()

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("liveon-bot")

# ─── Configuração ─────────────────────────────────────────────────────────────

DEFAULT_TICKETTOOL_ID = 557628352828014614
NICK_FIELD_NAME       = "qual é o seu nick no jogo?"
STAFF_ROLE_ID         = 1513030806744989872

# ─── Embeds do tutorial ───────────────────────────────────────────────────────

def embed_passo_1() -> discord.Embed:
    e = discord.Embed(
        title="⚔️ Recrutamento (1/4)",
        description=(
            "### Bem-vindo ao Live ON 🇧🇷\n"
            "**Comunidade brasileira de OSRS Social/PVM **\n"
            "Para seguir com seu apply, leia as informações das próximas etapas. "
            "Nelas você encontrará como funciona o clã, nossas integrações com o Discord "
            "e outras informações importantes para novos membros."
        ),
        color=65336,
    )
    e.set_image(url="https://i.imgur.com/JzFN0g2.png")
    e.add_field(name=" **Requisitos mínimos:**", value="- 150 Quest points\n- 1500 Total level", inline=True)
    e.add_field(name="**Regras:**", value="<#1069666477470388254>", inline=True)
    return e

def embed_passo_2() -> discord.Embed:
    e = discord.Embed(
        title="⚔️ Recrutamento (2/4)",
        description=(
            "**Ative todos os canais do Discord**\n"
            "Tudo o que acontece no nosso clã é divulgado aqui no Discord: anúncios, eventos, sorteios, "
            "avisos importantes etc.\n\n"
            "Para não perder nenhuma novidade, recomendamos que você ative a visualização de todos os "
            "canais do servidor.\n\n"
            "**Como fazer:**\nClique no nome do servidor → Mostrar todos os canais."
        ),
        color=65336,
    )
    e.set_image(url="https://i.imgur.com/MAleNyG.gif")
    return e

def embed_passo_3() -> discord.Embed:
    e = discord.Embed(
        title="⚔️ Recrutamento (3/4)",
        description=(
            "### Plugins:\n"
            "*Alguns plugins que utilizamos para melhorar a experiência e a integração do clã com o Discord. "
            "A instalação é opcional, mas é altamente recomendada para que você tenha acesso a todas as "
            "funcionalidades utilizadas pelo clã.*\n\n"
            "- **DropTracker**\n"
            "<#1511935967953424517>\n"
            "Para participar do leaderboard de drops e concorrer ao MVP mensal\n"
            "*Instalação:\nPlugin Hub → DropTracker → Install. Não é necessário configurar nada."
        ),
        color=65336,
    )
    e.set_image(url="https://i.imgur.com/avjCEdx.png")
    e.add_field(
        name=" ",
        value=(
            "- **Dink**\n"
            "<#956154770077417472>\n"
            "Para seus drops e pets serem enviados automaticamente aqui no discord, "
            "utilize o plugin Dink\n"
            "*Video ensinando a configurar o dink aqui: "
            "[Link](https://discord.com/channels/956153870181085204/956154770077417472/1514406061312966797)*\n"
            "Dynamic config URL:\n"
            "```https://raw.githubusercontent.com/MilicoOSRS/dink/refs/heads/main/config.json```"
        ),
    )
    return e

def embed_passo_4() -> discord.Embed:
    e = discord.Embed(
        title="⚔️ Recrutamento (4/4)",
        description=(
            "### Ranks\n"
            "Nosso sistema de ranks é baseado no progresso da sua conta, medido por Horas Jogadas (EHP), "
            "Horas de Boss (EHB) e marcos importantes no jogo, como Quest Cape e Achievement Diary Cape. "
            "Também contamos com ranks especiais para os MVPs do mês e Colaboradores.\n"
            "<#1253747276564660296>\n"
        ),
        color=65336,
    )
    e.set_image(url="https://i.imgur.com/x70WCFP.png")
    e.add_field(
        name="Para novos membros:",
        value=(
            "<:atencao:1303805885109371021> É necessário estar no clã há pelo menos **30 dias** "
            "para poder solicitar seu primeiro rank.\n"
        ),
    )
    return e

def embed_final() -> discord.Embed:
    e = discord.Embed(
        title="⚔️ Recrutamento ✅",
        description=(
            "### Tudo pronto!\n"
            "Seja bem-vindo(a) ao Live ON! Esperamos que você aproveite nossa comunidade e "
            "compartilhe muitos drops e conquistas conosco.\n\n"
            "**Clique no botão abaixo para chamar algum staff e concluir seu apply dentro do jogo.**\n"
        ),
        color=65336,
    )
    e.set_image(url=(
        "https://media.discordapp.net/attachments/1264778726332301404/1444372967940161708/image.png"
        "?ex=6a4c8866&is=6a4b36e6&hm=d4da8de1a2d87b5ab9a0ad38ac6c483b3dbf6a9fea461e2a9eb59b9eb460ce5b"
        "&=&format=webp&quality=lossless"
    ))
    return e

# Lista ordenada dos passos
TUTORIAL_STEPS = [embed_passo_1, embed_passo_2, embed_passo_3, embed_passo_4]

# ─── Views com callbacks ──────────────────────────────────────────────────────
# Cada View é criada por mensagem e guarda o user_id do dono do ticket.
# Os callbacks são métodos da própria View, evitando o conflito de duplo-dispatch
# que ocorre ao misturar on_interaction com o sistema interno de Views.

class TutorialView(discord.ui.View):
    """View de navegação para os passos numerados (1/4 … 4/4)."""

    def __init__(self, current_index: int, user_id: int):
        super().__init__(timeout=None)
        self.current_index = current_index
        self.user_id = user_id
        self._add_buttons()

    def _add_buttons(self):
        is_first = self.current_index == 0
        is_last  = self.current_index == len(TUTORIAL_STEPS) - 1

        if not is_first:
            back = discord.ui.Button(
                label="← Voltar",
                style=discord.ButtonStyle.secondary,
                custom_id=f"tut_{self.current_index - 1}_{self.user_id}",
            )
            back.callback = self._make_nav_cb(self.current_index - 1)
            self.add_item(back)

        if is_last:
            nxt = discord.ui.Button(
                label="Próximo →",
                style=discord.ButtonStyle.success,
                custom_id=f"tut_final_{self.user_id}",
            )
            nxt.callback = self._make_final_cb()
        else:
            nxt = discord.ui.Button(
                label="Próximo →",
                style=discord.ButtonStyle.success,
                custom_id=f"tut_{self.current_index + 1}_{self.user_id}",
            )
            nxt.callback = self._make_nav_cb(self.current_index + 1)
        self.add_item(nxt)

    def _make_nav_cb(self, target: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(
                    "Apenas quem abriu o ticket pode navegar neste tutorial.", ephemeral=True
                )
                return
            view = TutorialView(target, self.user_id)
            await interaction.response.edit_message(embed=TUTORIAL_STEPS[target](), view=view)
            log.info(f"Usuário {self.user_id}: navegou para passo {target + 1}")
        return callback

    def _make_final_cb(self):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(
                    "Apenas quem abriu o ticket pode navegar neste tutorial.", ephemeral=True
                )
                return
            view = FinalView(self.user_id)
            await interaction.response.edit_message(embed=embed_final(), view=view)
            log.info(f"Usuário {self.user_id}: embed final exibido")
        return callback


class FinalView(discord.ui.View):
    """View do embed final com botões Voltar e Concluir."""

    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

        back = discord.ui.Button(
            label="← Voltar",
            style=discord.ButtonStyle.secondary,
            custom_id=f"tut_back_final_{user_id}",
        )
        back.callback = self._back_cb
        self.add_item(back)

        done = discord.ui.Button(
            label="Concluir ✓",
            style=discord.ButtonStyle.success,
            custom_id=f"tut_done_{user_id}",
        )
        done.callback = self._done_cb
        self.add_item(done)

    async def _back_cb(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Apenas quem abriu o ticket pode navegar neste tutorial.", ephemeral=True
            )
            return
        last = len(TUTORIAL_STEPS) - 1
        view = TutorialView(last, self.user_id)
        await interaction.response.edit_message(embed=TUTORIAL_STEPS[last](), view=view)
        log.info(f"Usuário {self.user_id}: voltou do embed final para passo {last + 1}")

    async def _done_cb(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Apenas quem abriu o ticket pode clicar neste botão.", ephemeral=True
            )
            return
        # Remove os botões
        await interaction.response.edit_message(view=None)
        # Pinga o staff
        await interaction.channel.send(
            f"<@&{STAFF_ROLE_ID}> — <@{self.user_id}> concluiu as etapas e está pronto para o apply! ✅"
        )
        log.info(f"Staff pingado para usuário {self.user_id}")

# ─── Helpers ──────────────────────────────────────────────────────────────────

def to_channel_name(nick: str) -> str:
    name = nick.lower()
    name = re.sub(r'\s+', '-', name)
    name = re.sub(r'[^a-z0-9\-_]', '', name)
    name = re.sub(r'-{2,}', '-', name)
    name = name.strip('-')
    return "apply-" + name[:93]

def extract_nick(embeds: list[discord.Embed]) -> str | None:
    for embed in embeds:
        if embed.description:
            m = re.search(
                r'\*\*Qual é o seu nick no jogo\?\*\*\s*```\n?([\s\S]*?)```',
                embed.description,
                re.IGNORECASE,
            )
            if m and m.group(1).strip():
                return m.group(1).strip()
        for field in embed.fields:
            if field.name.strip().lower() == NICK_FIELD_NAME and field.value.strip():
                return field.value.strip()
    return None

def extract_user_id(message: discord.Message) -> int | None:
    if message.mentions:
        return message.mentions[0].id
    for embed in message.embeds:
        if embed.description:
            m = re.search(r'<@!?(\d+)>', embed.description)
            if m:
                return int(m.group(1))
    return None

# ─── Bot ──────────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

TICKETTOOL_BOT_ID = int(os.getenv("TICKETTOOL_BOT_ID", str(DEFAULT_TICKETTOOL_ID)))

@client.event
async def on_ready():
    log.info(f"Bot conectado: {client.user} (ID: {client.user.id})")
    log.info(f"Monitorando TicketTool ID: {TICKETTOOL_BOT_ID}")

@client.event
async def on_message(message: discord.Message):
    if message.author.id != TICKETTOOL_BOT_ID:
        return
    if not message.embeds or not message.guild:
        return

    nick = extract_nick(message.embeds)
    if not nick:
        return

    user_id = extract_user_id(message)
    if not user_id:
        log.warning(f"Nick encontrado mas sem usuário mencionado (msg {message.id})")
        return

    # Renomeia o canal
    try:
        await message.channel.edit(name=to_channel_name(nick), reason="TicketTool: nick do jogador")
        log.info(f"Canal renomeado para {to_channel_name(nick)}")
    except Exception as exc:
        log.error(f"Falha ao renomear canal: {exc}")

    # Altera apelido
    try:
        member = message.guild.get_member(user_id) or await message.guild.fetch_member(user_id)
        await member.edit(nick=nick, reason="TicketTool: resposta do modal de ticket")
        log.info(f"Apelido de {member} alterado para '{nick}'")
    except Exception as exc:
        log.error(f"Falha ao alterar apelido: {exc}")

        # Envia tutorial (passo 1)
    try:
        # Verifica se o tutorial já foi enviado neste ticket
        async for msg in message.channel.history(limit=25):
            if (
                msg.author.id == client.user.id
                and msg.embeds
                and msg.embeds[0].title == "⚔️ Recrutamento (1/4)"
            ):
                log.info("Tutorial já existe neste ticket. Ignorando.")
                return

        await message.channel.send(
            embed=TUTORIAL_STEPS[0](),
            view=TutorialView(0, user_id),
        )

        log.info(f"Tutorial enviado no canal {message.channel.id} para usuário {user_id}")

    except Exception as exc:
        log.error(f"Falha ao enviar tutorial: {exc}")

# ─── Entry point ──────────────────────────────────────────────────────────────

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

client.run(TOKEN, log_handler=None)
