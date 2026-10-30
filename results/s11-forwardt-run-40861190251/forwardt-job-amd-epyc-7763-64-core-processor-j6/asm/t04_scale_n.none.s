0000000000001220 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m>:
    1220:	test   %rdx,%rdx
    1223:	je     12df <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xbf>
    1229:	mov    (%rsi),%rax
    122c:	mov    (%rdi),%rcx
    122f:	xor    %esi,%esi
    1231:	cmp    $0x8,%rdx
    1235:	jb     127c <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x5c>
    1237:	mov    %rcx,%rdi
    123a:	sub    %rax,%rdi
    123d:	cmp    $0x20,%rdi
    1241:	jb     127c <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x5c>
    1243:	mov    %rdx,%rsi
    1246:	and    $0xfffffffffffffff8,%rsi
    124a:	xor    %edi,%edi
    124c:	nopl   0x0(%rax)
    1250:	movdqu (%rax,%rdi,4),%xmm0
    1255:	movdqu 0x10(%rax,%rdi,4),%xmm1
    125b:	paddd  %xmm0,%xmm0
    125f:	paddd  %xmm1,%xmm1
    1263:	movdqu %xmm0,(%rcx,%rdi,4)
    1268:	movdqu %xmm1,0x10(%rcx,%rdi,4)
    126e:	add    $0x8,%rdi
    1272:	cmp    %rdi,%rsi
    1275:	jne    1250 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x30>
    1277:	cmp    %rdx,%rsi
    127a:	je     12df <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xbf>
    127c:	mov    %rdx,%r8
    127f:	mov    %rsi,%rdi
    1282:	and    $0x3,%r8
    1286:	je     12a3 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x83>
    1288:	mov    %rsi,%rdi
    128b:	nopl   0x0(%rax,%rax,1)
    1290:	mov    (%rax,%rdi,4),%r9d
    1294:	add    %r9d,%r9d
    1297:	mov    %r9d,(%rcx,%rdi,4)
    129b:	inc    %rdi
    129e:	dec    %r8
    12a1:	jne    1290 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x70>
    12a3:	sub    %rdx,%rsi
    12a6:	cmp    $0xfffffffffffffffc,%rsi
    12aa:	ja     12df <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0xbf>
    12ac:	nopl   0x0(%rax)
    12b0:	mov    (%rax,%rdi,4),%esi
    12b3:	add    %esi,%esi
    12b5:	mov    %esi,(%rcx,%rdi,4)
    12b8:	mov    0x4(%rax,%rdi,4),%esi
    12bc:	add    %esi,%esi
    12be:	mov    %esi,0x4(%rcx,%rdi,4)
    12c2:	mov    0x8(%rax,%rdi,4),%esi
    12c6:	add    %esi,%esi
    12c8:	mov    %esi,0x8(%rcx,%rdi,4)
    12cc:	mov    0xc(%rax,%rdi,4),%esi
    12d0:	add    %esi,%esi
    12d2:	mov    %esi,0xc(%rcx,%rdi,4)
    12d6:	add    $0x4,%rdi
    12da:	cmp    %rdi,%rdx
    12dd:	jne    12b0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x90>
    12df:	ret
