#!/bin/bash
set -e
WGDIR=${1:-/etc/wireguard}
BACKUP_DIR=${2:-/var/backups/wg_keys}
mkdir -p "$BACKUP_DIR"
if [ -f "$WGDIR/server_private.key" ]; then
  cp "$WGDIR/server_private.key" "$BACKUP_DIR/server_private.key.$(date +%s)"
fi
# generate and replace with new keys
newpriv=$(wg genkey)
newpub=$(echo "$newpriv" | wg pubkey)
echo "$newpriv" > "$WGDIR/server_private.key"
echo "$newpub" > "$WGDIR/server_public.key"
# reload wg
wg syncconf wg0 <(wg-quick strip wg0)
systemctl restart wg-quick@wg0