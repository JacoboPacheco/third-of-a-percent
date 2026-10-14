0000000000001240 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rdx
    1247:	mov    %rdx,%rsi
    124a:	sub    %rax,%rsi
    124d:	mov    (%rdi),%rcx
    1250:	mov    0x8(%rdi),%rdi
    1254:	sub    %rcx,%rdi
    1257:	cmp    %rsi,%rdi
    125a:	jb     1360 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x120>
    1260:	cmp    %rax,%rdx
    1263:	je     1354 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    1269:	sar    $0x2,%rsi
    126d:	cmp    $0x8,%rsi
    1271:	jb     12e2 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa2>
    1273:	mov    %rax,%rdx
    1276:	sub    %rcx,%rdx
    1279:	cmp    $0x20,%rdx
    127d:	jb     12e2 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa2>
    127f:	mov    %rsi,%rdi
    1282:	and    $0xfffffffffffffff8,%rdi
    1286:	mov    %esi,%edx
    1288:	and    $0x7,%edx
    128b:	lea    (%rax,%rsi,4),%r8
    128f:	add    $0xfffffffffffffff0,%r8
    1293:	lea    (%rcx,%rsi,4),%r9
    1297:	add    $0xfffffffffffffff0,%r9
    129b:	mov    %rdi,%r10
    129e:	neg    %r10
    12a1:	xor    %r11d,%r11d
    12a4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b0:	movdqu -0x10(%r8,%r11,4),%xmm0
    12b7:	movdqu (%r8,%r11,4),%xmm1
    12bd:	paddd  %xmm1,%xmm1
    12c1:	paddd  %xmm0,%xmm0
    12c5:	movdqu %xmm1,(%r9,%r11,4)
    12cb:	movdqu %xmm0,-0x10(%r9,%r11,4)
    12d2:	add    $0xfffffffffffffff8,%r11
    12d6:	cmp    %r11,%r10
    12d9:	jne    12b0 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    12db:	cmp    %rdi,%rsi
    12de:	jne    12e5 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa5>
    12e0:	jmp    1354 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    12e2:	mov    %rsi,%rdx
    12e5:	lea    -0x1(%rdx),%rdi
    12e9:	mov    %rdx,%r8
    12ec:	and    $0x3,%r8
    12f0:	je     1355 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x115>
    12f2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1300:	lea    -0x1(%rdx),%rsi
    1304:	mov    -0x4(%rax,%rdx,4),%r9d
    1309:	add    %r9d,%r9d
    130c:	mov    %r9d,-0x4(%rcx,%rdx,4)
    1311:	mov    %rsi,%rdx
    1314:	dec    %r8
    1317:	jne    1300 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1319:	cmp    $0x3,%rdi
    131d:	jb     1354 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    131f:	nop
    1320:	mov    -0x4(%rax,%rsi,4),%edx
    1324:	add    %edx,%edx
    1326:	mov    %edx,-0x4(%rcx,%rsi,4)
    132a:	mov    -0x8(%rax,%rsi,4),%edx
    132e:	add    %edx,%edx
    1330:	mov    %edx,-0x8(%rcx,%rsi,4)
    1334:	mov    -0xc(%rax,%rsi,4),%edx
    1338:	add    %edx,%edx
    133a:	mov    %edx,-0xc(%rcx,%rsi,4)
    133e:	mov    -0x10(%rax,%rsi,4),%edx
    1342:	add    %edx,%edx
    1344:	mov    %edx,-0x10(%rcx,%rsi,4)
    1348:	lea    -0x4(%rsi),%rdx
    134c:	mov    %rdx,%rsi
    134f:	test   %rdx,%rdx
    1352:	jne    1320 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xe0>
    1354:	ret
    1355:	mov    %rdx,%rsi
    1358:	cmp    $0x3,%rdi
    135c:	jae    1320 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xe0>
    135e:	jmp    1354 <_Z12kern_m04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x114>
    1360:	ud2
    1362:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
