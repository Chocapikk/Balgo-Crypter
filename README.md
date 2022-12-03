

# Balgo Crypter

![](images/banner.png)

Balgo Crypter est un utilitaire de génération de charge utile de shell inverse codée Xor avec héxadécimal. Balgo Crypter a été développé par [Valentin Lobstein](https://github.com/Chocapikk).

## Installation

Téléchargez le fichier **balgo_crypter.py** et exécutez-le en utilisant Python 3.

```sh
python3 balgo_crypter.py
```

## Utilisation

Balgo Crypter peut prendre une commande de shell inverse et générer une charge utile à partir de cette commande.

```sh
python3 balgo_crypter.py -lh <host> -lp <port> -o <output_file>
```

Si un fichier d'entrée est spécifié, la commande de shell inverse sera extraite de ce fichier.

```sh
python3 balgo_crypter.py -lh <host> -lp <port> -i <input_file> -o <output_file>
```

## Exemple

Voici un exemple du résultat obtenu avec Balgo Crypter.

```sh
python3 balgo_crypter.py -lh 127.0.0.1 -lp 1234 -o out.py
```

![](images/example1.png)

Le fichier **out.py** contiendra les commandes données ci-dessous.

![](images/example2.png)

## Remerciements

Ce programme a été réalisé avec l'aide du projet [Openai Playground](https://github.com/openai/playground).
