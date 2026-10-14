0000000000001240 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rsi
    1247:	mov    %rsi,%r8
    124a:	sub    %rax,%r8
    124d:	je     12f4 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb4>
    1253:	mov    0x8(%rdi),%rdi
    1257:	add    $0xfffffffffffffffc,%r8
    125b:	cmp    $0x1c,%r8
    125f:	jb     12d4 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x94>
    1261:	mov    %rsi,%rcx
    1264:	sub    %rdi,%rcx
    1267:	cmp    $0x20,%rcx
    126b:	jb     12d4 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x94>
    126d:	shr    $0x2,%r8
    1271:	inc    %r8
    1274:	mov    %r8,%r9
    1277:	and    $0xfffffffffffffff8,%r9
    127b:	lea    0x0(,%r9,4),%r10
    1283:	mov    %rsi,%rcx
    1286:	sub    %r10,%rcx
    1289:	mov    %rdi,%rdx
    128c:	sub    %r10,%rdx
    128f:	mov    %r9,%r10
    1292:	neg    %r10
    1295:	xor    %r11d,%r11d
    1298:	nopl   0x0(%rax,%rax,1)
    12a0:	movdqu -0x20(%rsi,%r11,4),%xmm0
    12a7:	movdqu -0x10(%rsi,%r11,4),%xmm1
    12ae:	paddd  %xmm1,%xmm1
    12b2:	paddd  %xmm0,%xmm0
    12b6:	movdqu %xmm1,-0x10(%rdi,%r11,4)
    12bd:	movdqu %xmm0,-0x20(%rdi,%r11,4)
    12c4:	add    $0xfffffffffffffff8,%r11
    12c8:	cmp    %r11,%r10
    12cb:	jne    12a0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>
    12cd:	cmp    %r9,%r8
    12d0:	jne    12da <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x9a>
    12d2:	jmp    12f4 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb4>
    12d4:	mov    %rsi,%rcx
    12d7:	mov    %rdi,%rdx
    12da:	add    $0xfffffffffffffffc,%rdx
    12de:	xchg   %ax,%ax
    12e0:	mov    -0x4(%rcx),%esi
    12e3:	add    $0xfffffffffffffffc,%rcx
    12e7:	add    %esi,%esi
    12e9:	mov    %esi,(%rdx)
    12eb:	add    $0xfffffffffffffffc,%rdx
    12ef:	cmp    %rax,%rcx
    12f2:	jne    12e0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    12f4:	ret
    12f5:	data16 cs nopw 0x0(%rax,%rax,1)
