# NOTICE

**Infinite Cut is a modified version of Concat.**

Concat is a free, open-source video editor by Jareer ([@jub0t](https://github.com/jub0t))
and the Concat contributors, published at <https://github.com/jub0t/concat>
under the GNU Affero General Public License, version 3 or later.

Infinite Cut is a fork of that work, maintained by Infinite Minds Academy.
It is **not** Concat, is not endorsed by the Concat project, and bug reports
about it should come here rather than upstream.

This file is the notice the AGPL asks a modified version to carry
(section 5(a): a modified work must carry prominent notices stating that it
is modified, and when). Every copyright notice in the source is upstream's
and has been left exactly as it was.

## Licence

Infinite Cut is licensed under the **GNU Affero General Public License,
version 3 or later** — the same licence as the work it is derived from. The
full text is in [`LICENSE`](LICENSE), with the plugin exception in
[`LICENSE-EXCEPTIONS.md`](LICENSE-EXCEPTIONS.md).

In practice that means anyone who receives a copy of Infinite Cut — as an
installer, a package, or over a network — is entitled to the complete
corresponding source code of the version they received, under the same
licence. Relicensing it, shipping it closed-source, or distributing a build
whose source is not published is not permitted by the licence this code
arrives under.

Third-party components keep their own licences; see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

## What was changed, and when

Forked from Concat **0.2.7** on **15 October 2026**.

**Named and marked as its own product.** The editor, the engine crates, the
command-line driver and the installers are called Infinite Cut. The
application identifier is `online.aisolution.infinitecut`, which is also the
name of its settings and data folders, so Infinite Cut and Concat can be
installed side by side without touching each other's state. The Windows
installer carries new product GUIDs for the same reason: the old ones would
have made it upgrade over an installed Concat.

Concat's trademark policy asks that a modified build be given its own name
and its own icon, and that is what this is.

**New artwork.** Every logo, icon and launcher image is original work made
for Infinite Cut. None of Concat's artwork is used: the AGPL grants no
trademark rights, and Concat's name and logo were deliberately kept out of
that grant.

**Repointed services.** The update check reads this fork's releases, not
upstream's. The gRPC service is `infinitecut.v1.InfiniteCut`, so a client
written for one is not silently pointed at the other.

**Removed.** Upstream's contributor licence agreement, trademark policy,
code-signing policy, release audit log, translated READMEs and sponsor
material — all of which describe the Concat project rather than this one.

**Deliberately left alone.** Effect identifiers (`concat.blur`,
`concat.dissolve`, and the rest) and the `concat.json` project manifest keep
their names. They are written into saved projects and into every effect
package, and renaming them would orphan the effect catalogue and stop
Infinite Cut from opening projects made in Concat. They are never shown to a
user. For the same reason, downloadable AI models are still fetched from
upstream's release assets, which is where those files actually live; nothing
about that is hidden, and it can be repointed at a mirror of this project's
own at any time (`models.rs`).

Upstream issue links in source comments are also left as they are. They
explain why particular code looks the way it does, and rewriting them would
make the comments point at nothing.

## Upstream

If Infinite Cut is useful, Concat is the reason. Upstream is at
<https://github.com/jub0t/concat>; its releases, its issue tracker and its
Discord are the right place for anything about Concat itself.
