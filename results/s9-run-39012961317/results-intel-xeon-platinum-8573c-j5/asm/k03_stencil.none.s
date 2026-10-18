0000000000001220 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%r10
    1227:	mov    %r10,%r9
    122a:	sub    %rax,%r9
    122d:	mov    %r9,%rcx
    1230:	sar    $0x2,%rcx
    1234:	cmp    $0x3,%rcx
    1238:	jb     1357 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    123e:	mov    (%rdi),%rdx
    1241:	lea    -0x2(%rcx),%r8
    1245:	mov    $0x1,%edi
    124a:	mov    $0x2,%esi
    124f:	cmp    $0x8,%r8
    1253:	jb     12d9 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    1259:	lea    0x4(%rdx),%r11
    125d:	cmp    %r10,%r11
    1260:	jae    126e <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x4e>
    1262:	add    %rdx,%r9
    1265:	add    $0xfffffffffffffffc,%r9
    1269:	cmp    %r9,%rax
    126c:	jb     12d9 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xb9>
    126e:	mov    %r8,%r9
    1271:	and    $0xfffffffffffffff8,%r9
    1275:	lea    0x2(%r9),%rsi
    1279:	lea    0x1(%r9),%rdi
    127d:	xor    %r10d,%r10d
    1280:	movdqu (%rax,%r10,4),%xmm0
    1286:	movdqu 0x4(%rax,%r10,4),%xmm1
    128d:	paddd  %xmm0,%xmm1
    1291:	movdqu 0x8(%rax,%r10,4),%xmm0
    1298:	paddd  %xmm1,%xmm0
    129c:	movdqu 0x10(%rax,%r10,4),%xmm1
    12a3:	movdqu 0x14(%rax,%r10,4),%xmm2
    12aa:	paddd  %xmm1,%xmm2
    12ae:	movdqu 0x18(%rax,%r10,4),%xmm1
    12b5:	paddd  %xmm2,%xmm1
    12b9:	movdqu %xmm0,0x4(%rdx,%r10,4)
    12c0:	movdqu %xmm1,0x14(%rdx,%r10,4)
    12c7:	add    $0x8,%r10
    12cb:	cmp    %r10,%r9
    12ce:	jne    1280 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x60>
    12d0:	cmp    %r9,%r8
    12d3:	je     1357 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    12d9:	mov    %ecx,%r8d
    12dc:	sub    %esi,%r8d
    12df:	lea    0x1(%rsi),%r9
    12e3:	test   $0x1,%r8b
    12e7:	jne    12f6 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd6>
    12e9:	mov    %rsi,%r8
    12ec:	mov    %rdi,%rsi
    12ef:	cmp    %r9,%rcx
    12f2:	jne    130f <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xef>
    12f4:	jmp    1357 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    12f6:	mov    (%rax,%rdi,4),%r8d
    12fa:	add    -0x4(%rax,%rdi,4),%r8d
    12ff:	add    (%rax,%rsi,4),%r8d
    1303:	mov    %r8d,(%rdx,%rdi,4)
    1307:	mov    %r9,%r8
    130a:	cmp    %r9,%rcx
    130d:	je     1357 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x137>
    130f:	neg    %rcx
    1312:	inc    %r8
    1315:	data16 cs nopw 0x0(%rax,%rax,1)
    1320:	mov    (%rax,%rsi,4),%edi
    1323:	add    -0x4(%rax,%rsi,4),%edi
    1327:	add    -0x4(%rax,%r8,4),%edi
    132c:	mov    %edi,(%rdx,%rsi,4)
    132f:	mov    -0x4(%rax,%r8,4),%esi
    1334:	add    -0x8(%rax,%r8,4),%esi
    1339:	add    (%rax,%r8,4),%esi
    133d:	mov    %esi,-0x4(%rdx,%r8,4)
    1342:	lea    (%rcx,%r8,1),%rdi
    1346:	add    $0x2,%rdi
    134a:	mov    %r8,%rsi
    134d:	add    $0x2,%r8
    1351:	cmp    $0x1,%rdi
    1355:	jne    1320 <_Z16kern_k03_stencilRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x100>
    1357:	ret
    1358:	nopl   0x0(%rax,%rax,1)
