# This repository has been migrated to the self-hosted ari-web Forgejo instance: <https://git.ari.lt/ari.lt/trie.ari.lt>
# This repository has been migrated to the self-hosted ari-web Forgejo instance: <https://git.ari.lt/ari/trie.ari.lt>
# trie.ari.lt

> Public Markov chain.

# Requirements

-   Libtrie: <https://github.com/TruncatedDinoSour/libtrie> (<https://ari.lt/gh/libtrie>)
-   Memcached

# Running

```sh
export CFLAGS='-O3 -s -ffast-math'
make -j$(nproc) strip
su -c 'make install'
trie-update model.bin <init.txt
mv model.bin src/
python3 -m virtualenv venv && source venv/bin/activate
pip install -r requirements.txt && pip install gunicorn
./run.sh & disown
```

It'll now be running on `127.0.0.1:27123`.

# Credits

-   Init data (init.txt) is taken from chapter one of a public domain book "AN INTRODUCTION TO MATHEMATICS" By A. N. WHITEHEAD, Sc.D., F.R.S: <https://www.gutenberg.org/files/41568/41568-pdf.pdf> (<https://www.gutenberg.org/ebooks/41568>)
