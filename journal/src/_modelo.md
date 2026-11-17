---
title: título do post
date: 2026-01-01
description: uma linha que aparece na lista de posts e no feed rss
tags: tag-um, tag-dois
image: capa.webp
draft: true
---

Este arquivo é só um modelo: nomes que começam com `_` não são publicados. O campo `image` é opcional (vira a imagem de compartilhamento; sem ele, vale a primeira imagem do texto).

Arquivos do post (imagens, gráficos, páginas de artefatos) ficam na pasta `journal/src/<slug>/` e são citados só pelo nome.

## texto

Escreva em Markdown: **negrito**, *itálico*, [links](https://example.com), listas, citações e notas de rodapé.[^1]

[^1]: A nota aparece no fim do post.

> citações viram esse bloco com a linha amarela.

## imagens e gráficos

![descrição da imagem](foto.webp "legenda opcional, aparece embaixo")

Um gráfico com versão para cada tema (o site mostra a certa):

![gráfico, tema claro](grafico-claro.png){.only-light}
![gráfico, tema escuro](grafico-escuro.png "Figura 1. Legenda do gráfico."){.only-dark}

Clicar numa imagem abre ela em tela cheia.

## tabelas

| programa | período | registros |
|:---|:---|---:|
| exemplo a | 2013–2026 | 1.234.567 |
| exemplo b | 2020–2021 | 987.654 |

## avisos

> [!note] título opcional
> Tipos: `note`, `tip`, `warning`, `important` e `caution`. Aceita **markdown** dentro.

## código

```python
print("realçado, com botão de copiar")
```

Código recolhido, como no blog do rulio:

<details markdown="1">
<summary>código</summary>

```sql
SELECT 1;
```

</details>

## fórmulas

Em bloco: $$ E = mc^2 $$ e dentro da frase: \(a^2 + b^2 = c^2\).

## artefatos

Páginas HTML interativas (inclusive de artefatos do Claude) vão na pasta do post e entram assim:

<iframe src="artefato.html" height="420" title="descrição do artefato"></iframe>

Também funcionam `<video controls src="video.mp4"></video>`, `<audio controls src="audio.mp3"></audio>` e embeds externos (YouTube etc.) com `<iframe>`.
