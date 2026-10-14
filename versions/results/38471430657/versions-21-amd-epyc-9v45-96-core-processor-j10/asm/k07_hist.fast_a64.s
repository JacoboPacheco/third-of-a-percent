0000000000001240 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     1296 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x56>
    124c:	sar    $0x2,%rcx
    1250:	mov    (%rdi),%rdx
    1253:	mov    0x8(%rdi),%rsi
    1257:	sub    %rdx,%rsi
    125a:	sar    $0x2,%rsi
    125e:	xor    %edi,%edi
    1260:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    126f:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    127e:	xchg   %ax,%ax
    1280:	movzbl (%rax,%rdi,4),%r8d
    1285:	cmp    %r8,%rsi
    1288:	jbe    1297 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x57>
    128a:	incl   (%rdx,%r8,4)
    128e:	inc    %rdi
    1291:	cmp    %rdi,%rcx
    1294:	jne    1280 <_Z13kern_k07_histRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    1296:	ret
    1297:	ud2
    1299:	nopl   0x0(%rax)
