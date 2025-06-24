touch ~/.bashrc
curl -o- https://fnm.vercel.app/install | bash
eval $(fnm env --use-on-cd --shell bash)
fnm install 22 --corepack-enabled
fnm alias default 22

cd website
yarn
yarn build
cp -r dist ../static
cd ..

rm -rf website
rm -rf ~/.fnm
rm -rf ~/.bashrc
