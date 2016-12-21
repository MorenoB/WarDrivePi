echo "Discard any changes..."
sudo git stash save --keep-index
sudo git stash drop
echo "Changes discarded!"

echo "Pulling latest dev version..."
sudo git pull origin dev
echo "Done!"