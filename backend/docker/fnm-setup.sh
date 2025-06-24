export SHELL="bash"

curl -o- https://fnm.vercel.app/install | bash
source /root/.bashrc

fnm install --lts
corepack enable

cd website
yarn
yarn build
cp -r dist ../static
cd ..

rm -rf website
rm -rf ~/.fnm
rm -rf ~/.bashrc
