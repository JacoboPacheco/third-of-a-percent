0000000000001230 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1230:	mov    (%rsi),%rax
    1233:	mov    0x8(%rsi),%rsi
    1237:	sub    %rax,%rsi
    123a:	je     1324 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    1240:	sar    $0x2,%rsi
    1244:	mov    (%rdi),%rcx
    1247:	cmp    $0x8,%rsi
    124b:	jb     12b2 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x82>
    124d:	mov    %rax,%rdx
    1250:	sub    %rcx,%rdx
    1253:	cmp    $0x20,%rdx
    1257:	jb     12b2 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x82>
    1259:	mov    %rsi,%rdi
    125c:	and    $0xfffffffffffffff8,%rdi
    1260:	mov    %esi,%edx
    1262:	and    $0x7,%edx
    1265:	lea    (%rax,%rsi,4),%r8
    1269:	add    $0xfffffffffffffff0,%r8
    126d:	lea    (%rcx,%rsi,4),%r9
    1271:	add    $0xfffffffffffffff0,%r9
    1275:	mov    %rdi,%r10
    1278:	neg    %r10
    127b:	xor    %r11d,%r11d
    127e:	xchg   %ax,%ax
    1280:	movdqu -0x10(%r8,%r11,4),%xmm0
    1287:	movdqu (%r8,%r11,4),%xmm1
    128d:	paddd  %xmm1,%xmm1
    1291:	paddd  %xmm0,%xmm0
    1295:	movdqu %xmm1,(%r9,%r11,4)
    129b:	movdqu %xmm0,-0x10(%r9,%r11,4)
    12a2:	add    $0xfffffffffffffff8,%r11
    12a6:	cmp    %r11,%r10
    12a9:	jne    1280 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x50>
    12ab:	cmp    %rdi,%rsi
    12ae:	jne    12b5 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x85>
    12b0:	jmp    1324 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    12b2:	mov    %rsi,%rdx
    12b5:	lea    -0x1(%rdx),%rdi
    12b9:	mov    %rdx,%r8
    12bc:	and    $0x3,%r8
    12c0:	je     1325 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf5>
    12c2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12d0:	lea    -0x1(%rdx),%rsi
    12d4:	mov    -0x4(%rax,%rdx,4),%r9d
    12d9:	add    %r9d,%r9d
    12dc:	mov    %r9d,-0x4(%rcx,%rdx,4)
    12e1:	mov    %rsi,%rdx
    12e4:	dec    %r8
    12e7:	jne    12d0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    12e9:	cmp    $0x3,%rdi
    12ed:	jb     1324 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
    12ef:	nop
    12f0:	mov    -0x4(%rax,%rsi,4),%edx
    12f4:	add    %edx,%edx
    12f6:	mov    %edx,-0x4(%rcx,%rsi,4)
    12fa:	mov    -0x8(%rax,%rsi,4),%edx
    12fe:	add    %edx,%edx
    1300:	mov    %edx,-0x8(%rcx,%rsi,4)
    1304:	mov    -0xc(%rax,%rsi,4),%edx
    1308:	add    %edx,%edx
    130a:	mov    %edx,-0xc(%rcx,%rsi,4)
    130e:	mov    -0x10(%rax,%rsi,4),%edx
    1312:	add    %edx,%edx
    1314:	mov    %edx,-0x10(%rcx,%rsi,4)
    1318:	lea    -0x4(%rsi),%rdx
    131c:	mov    %rdx,%rsi
    131f:	test   %rdx,%rdx
    1322:	jne    12f0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    1324:	ret
    1325:	mov    %rdx,%rsi
    1328:	cmp    $0x3,%rdi
    132c:	jae    12f0 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xc0>
    132e:	jmp    1324 <_Z12kern_k04_revRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xf4>
