0000000000001220 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     12f7 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd7>
    1230:	sar    $0x2,%rcx
    1234:	mov    (%rdi),%rdx
    1237:	cmp    $0x1,%rcx
    123b:	mov    %rcx,%rsi
    123e:	adc    $0x0,%rsi
    1242:	xor    %edi,%edi
    1244:	cmp    $0x8,%rcx
    1248:	jb     1290 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    124a:	mov    %rdx,%r8
    124d:	sub    %rax,%r8
    1250:	cmp    $0x20,%r8
    1254:	jb     1290 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x70>
    1256:	mov    %rsi,%rdi
    1259:	and    $0xfffffffffffffff8,%rdi
    125d:	xor    %r8d,%r8d
    1260:	movdqu (%rax,%r8,4),%xmm0
    1266:	movdqu 0x10(%rax,%r8,4),%xmm1
    126d:	paddd  %xmm0,%xmm0
    1271:	paddd  %xmm1,%xmm1
    1275:	movdqu %xmm0,(%rdx,%r8,4)
    127b:	movdqu %xmm1,0x10(%rdx,%r8,4)
    1282:	add    $0x8,%r8
    1286:	cmp    %r8,%rdi
    1289:	jne    1260 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    128b:	cmp    %rdi,%rsi
    128e:	je     12f7 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd7>
    1290:	mov    %rsi,%r9
    1293:	mov    %rdi,%r8
    1296:	and    $0x3,%r9
    129a:	je     12b3 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x93>
    129c:	mov    %rdi,%r8
    129f:	nop
    12a0:	mov    (%rax,%r8,4),%r10d
    12a4:	add    %r10d,%r10d
    12a7:	mov    %r10d,(%rdx,%r8,4)
    12ab:	inc    %r8
    12ae:	dec    %r9
    12b1:	jne    12a0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x80>
    12b3:	sub    %rsi,%rdi
    12b6:	cmp    $0xfffffffffffffffc,%rdi
    12ba:	ja     12f7 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xd7>
    12bc:	nopl   0x0(%rax)
    12c0:	mov    (%rax,%r8,4),%esi
    12c4:	add    %esi,%esi
    12c6:	mov    %esi,(%rdx,%r8,4)
    12ca:	mov    0x4(%rax,%r8,4),%esi
    12cf:	add    %esi,%esi
    12d1:	mov    %esi,0x4(%rdx,%r8,4)
    12d6:	mov    0x8(%rax,%r8,4),%esi
    12db:	add    %esi,%esi
    12dd:	mov    %esi,0x8(%rdx,%r8,4)
    12e2:	mov    0xc(%rax,%r8,4),%esi
    12e7:	add    %esi,%esi
    12e9:	mov    %esi,0xc(%rdx,%r8,4)
    12ee:	add    $0x4,%r8
    12f2:	cmp    %r8,%rcx
    12f5:	jne    12c0 <_Z19kern_t03_scale_sizeRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0xa0>
    12f7:	ret
    12f8:	nopl   0x0(%rax,%rax,1)
