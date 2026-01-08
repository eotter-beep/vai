gpgconf --launch gpg-agent
gpg -d .env.gpg > /dev/null
python .